import contextlib
import collections
import functools
import itertools
import sys
import threading
import time
from queue import PriorityQueue

from .compat import PY2, ENCODING
from .cursor import Cursor
from .compat import safe_text
from .utils import get_frames
from .models import HeaderItem, LineItem, SpinnerStates


# TODO: Maybe add additional spinners, right now we only care about one for
# simplicity.
Spinner = collections.namedtuple("Spinner", "frames interval")
default_spinner = Spinner("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏", 80)


class SpinnerControl(object):

    def __init__(self, interval=None, print_interval=None):
        self.line = 0
        self.lines = 0

        self._interval = interval
        self._print_interval = print_interval  # Needed to Pass Through to Children

    def move_up(self):
        Cursor.move_up()
        self.line -= 1

    def move_down(self):
        Cursor.move_down()
        self.line += 1

    def to_bottom(self):
        while self.line < self.lines:
            self.move_down()

    def to_top(self):
        while self.line > 0:
            self.move_up()

    def print(self, text):
        Cursor.write(text)
        self.line += 1

    def overwrite(self, text):
        Cursor.overwrite(text)
        self.line += 1


class SpinnerGroup(SpinnerControl):

    def __init__(self, text, color, base_indent=0, lock=None, **kwargs):
        super(SpinnerGroup, self).__init__(**kwargs)

        self._blocks = []

        self._base_indent = base_indent
        self._color = color

        # Initialize the Header Line
        self._text = text
        self._frame = None
        self._state = SpinnerStates.NOTSET

        # TODO: If we want to make spinner or frames dynamic, we should add
        # getters/setters for these properties.  Right now, we only have one
        # spinner, so we don't need them.
        self._spinner = default_spinner

        self._frames = get_frames(self._spinner)
        self._cycle = itertools.cycle(self._frames)

        self._stop_spin = threading.Event()
        self._stop_consume = threading.Event()

        self.queue = PriorityQueue()
        self.counter = collections.Counter()

        # Keeps track of first line, so we know when to increment tracker.line
        # from -1 to 0.  Otherwise, when we update the header line, we do not
        # know whether or not to increment the number of lines.
        self._initial = True

        self._spinner = None
        self._consumer = None
        self._stdout_lock = lock or threading.Lock()

    @contextlib.contextmanager
    def block(self, text):
        block = SpinnerGroup(
            text=safe_text(text),
            color=self._color,
            print_interval=self._print_interval,
            interval=self._interval,
            base_indent=self._base_indent + 1,
            lock=self._stdout_lock,
        )
        try:
            self.hold_for_children()
            time.sleep(2)
            block.start()
            self._blocks.append(block)
            yield block
        finally:
            block.done()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        # Avoid stop() execution for the 2nd time
        if self._spinner.is_alive() or self._consumer.is_alive():
            self.stop()
        return False  # Nothing is Handled

    def start(self):
        if sys.stdout.isatty():
            Cursor.hide()

        self._spinner = threading.Thread(target=self._spin)
        self._consumer = threading.Thread(target=self._consume)

        self._spinner.start()
        self._consumer.start()

    def done(self, text=None):
        """
        Stops the spinner thread and updates the header line state to reflect new
        text or state.  The state should not have been set to OK at this point,
        since only the completion of all tasks without ERROR or WARNING will
        prompt the state being OK.

        Sets the state to OK if an ERROR or WARNING has not occured in any
        of the group lines or sub lines.

        If provided, changes the header text.
        """
        self._change_state(state=SpinnerStates.OK)
        self._change_text(text=text)

        # Guaranteed to be Change because of OK State
        item = HeaderItem(
            text=self._text,
            state=self._state,
            frame=self._frame,
            color=self._color,
        )

        # This will be the highest priority header item, followed by the second
        # highest priority header item which stops the queue consumption.
        # This means that the last header item is guaranteed to print after all
        # lines have been written, and then queue consumption stops.
        # Keeping numbers negative guarantees there is no comparison issue.
        self.queue.put(((1, -2), item))
        self.queue.put(((1, -1), None))

        self.stop()

    def stop(self):
        """
        [x] TODO:
        --------
        Have to incorporate nested blocks as well
        Allow control from main spinner container..
        """
        self._stop_spin.set()
        self._stop_consume.set()

        self._spinner.join()
        self._consumer.join()

        self.to_bottom()
        self.move_down()

    def write(self, text, state=None):
        """
        Write a message underneath the last written message without changing
        the top level text or spinner.

        [x] TODO:
        -------
        We might also want to update _head_out() on a state change.
        """
        state = state or SpinnerStates.NOTSET

        state_changed = self._change_state(state=state)
        if state_changed:
            header = HeaderItem(
                state=self._state,
                frame=self._frame,
                text=self._text,
                color=self._color,
            )
            self._put_header(header)

        line = LineItem(
            text=text,
            state=state,
        )
        self._put_line(line)

    def error(self, text=None):
        self.fail(text=text)

    def fail(self, text=None):
        if text:
            self.write(text, state=SpinnerStates.FAIL)
        else:
            state_changed = self._change_state(state=SpinnerStates.FAIL)
            if state_changed:
                self._head_out()

    def warning(self, text=None):
        if text:
            self.write(text, state=SpinnerStates.WARNING)
        else:
            state_changed = self._change_state(state=SpinnerStates.WARNING)
            if state_changed:
                self._head_out()

    def _spin(self):
        while not self._stop_spin.is_set():
            spin_phase = next(self._cycle)
            self._frame = spin_phase

            header = HeaderItem(
                frame=spin_phase,
                text=self._text,
                state=self._state,
                color=self._color,
            )
            self._put_header(header)

    def _consume(self):
        while True:
            item = self.queue.get()
            if item[1] is None:
                break
            self._update_display(item[1])
            self.queue.task_done()

    def _put_header(self, header):
        ct = self.counter['header']
        self.queue.put(((1, ct), header))
        self.counter['header'] += 1

    def _put_line(self, line):
        ct = self.counter['line']
        self.queue.put(((0, ct), line))
        self.counter['line'] += 1

    def _update_display(self, item):
        if item.type == 'header':
            self.counter['header'] += 1
            self._head_out(item)
        else:
            self.counter['line'] += 1
            self._line_out(item)

    def _line_out(self, line):

        message = line.format(base_indent=self._base_indent)
        with self._stdout_lock:

            self.to_bottom()
            self.print(message)
            self.lines += 1
            self.to_top()

            if self._print_interval:
                time.sleep(self._print_interval)

    def _head_out(self, item):
        """
        Updates the top level header of the spinner group when either the header
        text changes or the spinner phase changes.

        [x] TODO:
        --------
        Wait until last frame to display state of last line.
        """
        output = item.format(base_indent=self._base_indent)

        if self._initial:
            with self._stdout_lock:
                self.print(output)
                self.lines += 1
                self._initial = False
        else:
            with self._stdout_lock:
                self.to_top()
                self.overwrite(output)

    def _change_text(self, text=None):
        """
        Changes the text in the header line immediately.
        """
        if text:
            if text != self._text:
                self._text = text
                return True
        return False

    def _change_state(self, state=None):
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

    def __repr__(self):
        repr_ = u"<Spinner frames={0!s}>".format(self._frames)
        if PY2:
            return repr_.encode(ENCODING)
        return repr_


class Spinner(object):

    def __init__(self, color, interval=None, print_interval=None):
        """
        [x] TODO:
        --------
        Might want to incorporate signal handling similarly to how Yaspin does
        it, although it is out of scope for the time being.

        Do we need an overall spinner thread lock along with individual thread
        locks for the groups?
        """
        self._groups = []
        self._color = color

        # Need to allow updating of spinner for all children/sub children if we
        # make this property dynamic/settable.
        self._spinner = default_spinner

        self._interval = (interval or self._spinner.interval) * 0.001  # Milliseconds to Seconds
        self._print_interval = print_interval * 0.001 if print_interval else 0  # Milliseconds to Seconds

    @contextlib.contextmanager
    def group(self, text):
        group = SpinnerGroup(
            text=safe_text(text),
            color=self._color,
            print_interval=self._print_interval,
            interval=self._interval,
        )
        Cursor.newline()
        group.start()
        self._groups.append(group)
        try:
            yield group
        finally:
            group.done()

    def __call__(self, fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)
        return inner

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        for group in self._groups:
            group.color = value