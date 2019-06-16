import contextlib
import itertools
import sys
import threading
import time

from termx.ext.compat import safe_text, PY2, ENCODING

from termx.core.terminal import Cursor
from termx.core.colorlib import color as Color

from ._utils import get_frames
from .models import HeaderItem, LineItem, SpinnerStates


class SpinnerMixin(object):

    def reset(self):
        self.base_indent = 0

    def base_indent(self, reenter=False, indent=None):
        """
        [x] TODO:
        --------
        Do we always want to reenter on the last level?  Or the level that
        we left off at?

        Not sure if this is right or not.
        """
        if reenter:
            return self._base_indent + 1
        elif indent:
            return self._base_indent + indent
        return self._base_indent

    def _group(self, text, reenter=False, indent=None):

        return SpinnerGroup(
            text=safe_text(text),
            color=self._color,
            spinner=self._spinner,
            options=self.options,
            base_indent=self.base_indent(reenter=reenter)
        )

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
        group = self._group(text, reenter=True)

        if separate:
            Cursor.newline()

        self.run_group(group)

    @contextlib.contextmanager
    def group(self, text, separate=True, indent=None):
        group = self._group(text, reenter=False, indent=indent)

        if separate:
            Cursor.newline()

        return self.run_group(group)

    def run_group(self, group):
        group.start()
        self._groups.append(group)
        try:
            yield group
        except Exception as e:
            group.error(str(e))
            raise e
        finally:
            group.done()

            # Should we remove groups as they finish?
            # self._groups.remove(group)


class SpinnerControl(object):

    def __init__(self, spinner, options):
        """
        [x] TODO:
        --------
        If we want to make spinner or frames dynamic, we should add
        getters/setters for these properties.  Right now, we only have one
        spinner, so we don't need them.
        """
        self.head = self.ln = False
        self.options = options

        self._spinner = spinner
        self._frames = get_frames(self._spinner)
        self._cycle = itertools.cycle(self._frames)

        self.lines = 0

    def overwrite(self, text):
        Cursor.clear_line()
        sys.stdout.write("%s" % text)
        sys.stdout.write("\r")

    def print_head(self, text):
        self.overwrite("%s" % text)

    def move_to_newline(self):
        i = 0
        while i < self.lines:
            Cursor.move_down()
            i += 1
        Cursor.newline()

    def move_to_head(self):
        i = 0
        while i < self.lines:
            Cursor.move_up()
            i += 1

    @contextlib.contextmanager
    def temporary_line(self):
        """
        Temporarily moves the cursor to a newline and then immediately back to
        the header line to keep animation smooth.
        """
        try:
            self.move_to_newline()
            self.lines += 1
            yield self
        finally:
            self.move_to_head()

    def print(self, text):
        with self.temporary_line():
            self.overwrite(text)


class SpinnerGroup(SpinnerControl, SpinnerMixin):

    def __init__(self, text, color, spinner, options, base_indent=0):
        super(SpinnerGroup, self).__init__(spinner, options)

        self._groups = []
        self._base_indent = base_indent

        self._color = color
        if not isinstance(self._color, Color):
            raise RuntimeError('SpinnerGroup must be initialized with color instance.')

        # Initialize the Header Line
        self._text = text
        self._frame = None
        self._state = SpinnerStates.NOTSET

        self._stop_spin = threading.Event()
        self._done = False

        self._spin_thread = None
        self._write_lock = threading.Lock()

    @contextlib.contextmanager
    def group(self, text, reenter=False, indent=None):
        """
        This is where the Spinner recursion occurs, since groups can create
        sub-context groups.
        """
        self.done()
        return super(SpinnerGroup, self).group(text, reenter=reenter, indent=1)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        # Avoid stop() execution for the 2nd time
        if self._spin_thread.is_alive() or self._consumer.is_alive():
            self.stop()
        return False  # Nothing is Handled

    def start(self):
        if sys.stdout.isatty():
            Cursor.hide()

        self._spin_thread = threading.Thread(target=self._spin)
        self._spin_thread.start()

    def _spin(self):
        while not self._stop_spin.is_set():
            spin_phase = next(self._cycle)
            time.sleep(self.options.spin_interval)
            self._change(frame=spin_phase)

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
            self._change(state=SpinnerStates.OK, text=text)
            self.stop()

    def stop(self):
        """
        [x] TODO:
        --------
        Have to incorporate nested blocks as well
        Allow control from main spinner container..
        """
        self._stop_spin.set()
        self._spin_thread.join()
        self.move_to_newline()

    def write(self, text, state=None, options=None):
        """
        Write a message underneath the last written message waithout changing
        the top level text or spinner.

        Only Updates Header on State Change Associated w/ Line
        """
        state = state or SpinnerStates.NOTSET
        line = LineItem(text=text, state=state, options=options)
        self._update_display(line)

        self._change(state)

    """
    [x] TODO:
    --------
    Allow errors, OK and warnings to be referenced JUST for the individual lines
    through the use of `propogate`, in which case they can be non-colored
    versions of the icons.

    We have to take a closer look at setting fail, error, etc. without text,
    should we allow that to just update the header?
    """

    def error(self, text=None, propogate=True):
        self.fail(text=text, propogate=propogate)

    def fail(self, text=None, propogate=True):
        if text:
            self.write(text, state=SpinnerStates.FAIL)
        else:
            self._change_state(state=SpinnerStates.FAIL)

    def warning(self, text=None, options=None):
        if text:
            self.write(text, state=SpinnerStates.WARNING, options=options)
        else:
            self._change_state(state=SpinnerStates.WARNING)

    def _change(self, state=None, text=None, frame=None, priority=None):

        state = state or SpinnerStates.NOTSET

        state_changed = self._change_state(state)
        frame_changed = self._change_frame(frame)
        text_changed = self._change_text(text)

        header = HeaderItem(
            text=self._text,
            state=self._state,
            frame=self._frame,
            color=self._color,
        )
        self._update_display(header)
        return (state_changed, text_changed, frame_changed)

    def _change_text(self, text):
        """
        Changes the text in the header line immediately.
        """
        if text:
            if text != self._text:
                self._text = text
                return True
        return False

    def _change_frame(self, frame):
        """
        Changes the text in the header line immediately.
        """
        if frame:
            if frame != self._frame:
                self._frame = frame
                return True
        return False

    def _change_state(self, state):
        """
        Changes the overall state of the spinnner group if the provided state
        is more severe (higher level) than the existing state.

        If the state is changed, the header line will be updated to reflect that
        once the group completes.  The line where a state change occurs will
        always reflect the state change.

        [x] Loading...
            > Write 1
            > Write 2
                ✘ An Error Occured  ->  State Changed to Error (Icon Set to ✘)

        After completion...

        ✘ Loading...  ->  Header Updated to Show Error Occured in Group
            > Write 1
            > Write 2
                ✘ An Error Occured  ->  State Changed to Error (Icon Set to ✘)
                > Write 1 After Error
                > Write 2 After Error
        """
        if state:
            if state.level != self._state.level:
                if state.level > self._state.level:
                    self._state = state
                    return True
        return False

    def _update_display(self, item):
        if item.type == 'header':
            self._head_out(item)
        else:
            self._line_out(item)

    def _line_out(self, line):
        message = line.format(base_indent=self._base_indent)
        time.sleep(self.options.write_interval)

        with self._write_lock:
            self.print(message)

    def _head_out(self, item):
        """
        Updates the top level header of the spinner group when either the header
        text changes or the spinner phase changes.

        [x] TODO:
        --------
        Wait until last frame to display state of last line.
        """
        output = item.format(base_indent=self._base_indent)
        with self._write_lock:
            self.print_head(output)

    def __repr__(self):
        repr_ = u"<Spinner frames={0!s}>".format(self._frames)
        if PY2:
            return repr_.encode(ENCODING)
        return repr_
