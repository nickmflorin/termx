import collections
import contextlib
import sys
import threading

from termx.ext.compat import ENCODING, PY2
from termx.core.terminal import Cursor
from termx.core.colorlib import color as Color

from .models import TerminalOptions, SpinnerStates, LineItem
from .base import AbstractSpinner, AbstractGroup


# TODO: Maybe add additional spinners, right now we only care about one for
# simplicity.
sp = collections.namedtuple("Spinner", "frames interval")
default_spinner = sp("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏", 80)


class Spinner(AbstractSpinner):

    def __init__(self, color='black', options=None):
        """
        [x] TODO:
        --------
        Might want to incorporate signal handling similarly to how Yaspin does
        it, although it is out of scope for the time being.

        Do we need an overall spinner thread lock along with individual thread
        locks for the groups?

        [x] TODO:
        --------
        Incorporate other spinners besides just the defalut one.
        """
        options = TerminalOptions(**(options or {}))
        color = Color(color)

        AbstractSpinner.__init__(
            self,
            color=color,
            options=options,
            spinner=default_spinner,
        )

    def _yield_descendants(self):

        def descend(child):
            if child._children:
                for child in child._children:
                    yield from descend(child)
            else:
                yield child

        yield from descend(self)

    def _find_youngest_descendant(self):
        descendants = list(self._yield_descendants())
        youngest = sorted(descendants,
            key=lambda child: (child._depth, child._index), reverse=True)
        return youngest[0]

    @contextlib.contextmanager
    def reenter(self, text, separate=False):
        """
        Reenter is useful when we have to leave the spinner context manager
        but want to return to the same level we were before:

        with spinner.group('First Group') as gp:
            gp.write('Message 1')
            gp.write('Message 2')

            with gp.group('Second Group') as gp:
                gp.write('Message 3')
                gp.write('Message 4')

        # Some Other Write Logic...

        with spinner.group('Third Group', reenter=True) as gp:
            gp.write('Message 5')

        The above would output something like:

        ✔ First Group
          > Message 1
          > Message 2
          ✔ Second Group
            > Message 3
            > Message 4
          ✔ Third Group
            > Message 5
        """
        if separate:
            Cursor.newline()

        youngest = self._find_youngest_descendant()
        with youngest._parent.child(text) as desc:
            yield desc

    @contextlib.contextmanager
    def child(self, text, separate=True):
        """
        [x] NOTE:
        --------
        In general, things do not seem to work as well for cases when we chain
        the context managers:

        >>> with self._child(text) as group:
        >>>     self._children.append(group)
        >>>     yield group

        Not sure why, but it does mess with things a tiny bit.
        """
        if separate:
            Cursor.newline()

        child = self._child(text)
        self._children.append(child)

        try:
            child.start()
            yield child
        finally:
            child.done()

    def __repr__(self):
        repr_ = u"<Spinner frames={0!s}>".format(self._frames)
        if PY2:
            return repr_.encode(ENCODING)
        return repr_


class SpinnerGroup(AbstractGroup):

    def __enter__(self):
        if self._parent and self._parent._quit:
            return None
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        # Avoid stop() execution for the 2nd time
        if exc_type:
            self._stop_spin.set()
            self._spin_thread.join()
            self._quit = True
            self.error(exc_val)
            self._move_to_newline()
            return 0

        if self._spin_thread.is_alive():
            self.stop()
        return False  # Nothing is Handled

    def start(self):
        if sys.stdout.isatty():
            Cursor.hide()

        self._spin_thread = threading.Thread(target=self._spin)
        self._spin_thread.start()

    @contextlib.contextmanager
    def child(self, text):
        """
        This is where the Spinner recursion occurs, since groups can create
        sub-context groups.

        [x] TODO:
        --------
        Figure out how to keep nested animation going, where we do not want
        to kill the top level thread while the children are running.

        [x] NOTE:
        --------
        In general, things do not seem to work as well for cases when we chain
        the context managers:

        >>> with self._child(text) as group:
        >>>     self._children.append(group)
        >>>     yield group

        Not sure why, but it does mess with things a tiny bit.
        """
        self.done()

        child = self._child(text)
        self._children.append(child)

        try:
            child.start()
            yield child
        finally:
            child.done()

    def hold(self):
        self._move_to_newline()

    def done(self, text=None):
        """
        Stops the spinner thread and updates the header line state to reflect new
        text or state.  The state should not have been set to OK at this point,
        since only the completion of all tasks without ERROR or WARNING will
        prompt the state being OK.

        Sets the state to OK, if...
            Guaranteed to be state change unless there was a line item with
            a WARNING or ERROR state, since those have higher levels than OK,
            in which case state is not set to OK.

        If provided, changes the header text.
        """
        if not self._done:
            self._done = True
            self.stop()
            self._change(state=SpinnerStates.OK, text=text)
            self._move_to_newline()

    def stop(self):
        """
        [x] TODO:
        --------
        Have to incorporate nested blocks as well
        Allow control from main spinner container..
        """
        # if not self._stopped:
        # self._stopped = True
        self._stop_spin.set()
        self._spin_thread.join()

    def write(self, text, state=None, options=None, fatal=True):
        """
        Write a message underneath the last written message waithout changing
        the top level text or spinner.

        Only Updates Header on State Change Associated w/ Line
        """
        state = state or SpinnerStates.NOTSET
        line = LineItem(
            text=text,
            state=state,
            depth=self._depth,
            options=options,
            fatal=fatal,
        )
        self._line_out(line)

    """
    [x] TODO:
    --------
    Allow errors, OK and warnings to be referenced JUST for the individual lines
    through the use of `propogate`, in which case they can be non-colored
    versions of the icons.

    We have to take a closer look at setting fail, error, etc. without text,
    should we allow that to just update the header?
    """

    def error(self, text=None, fatal=True):
        self.fail(text=text, fatal=fatal)

    def okay(self, text, options=None):
        """
        Writing a line as "okay" is always non-fatal, since the only way to
        make the top level header item have a state okay is if all tasks complete
        without an error or warning (that is fatal).

        This effectively just puts a checkmark next to the item.
        """
        options = options or {}
        options.update(color_icon=False)
        # Not Really Fatal - But just means don't color icon and use bullet too.
        self.write(text, state=SpinnerStates.OK, options=options, fatal=False)

    def fail(self, text=None, options=None, fatal=True):
        options = options or {}
        if text:
            self.write(text, state=SpinnerStates.FAIL, options=options, fatal=fatal)
        if fatal:
            self._change_state(state=SpinnerStates.FAIL)

    def warning(self, text=None, options=None, fatal=True):
        # if not self._parenting:
        #     raise SpinnerError('Cannot write with a spinner descendant that is not active.')
        options = options or {}
        if text:
            self.write(text, state=SpinnerStates.WARNING, options=options, fatal=fatal)
        if fatal:
            self._change_state(state=SpinnerStates.WARNING)
