import contextlib
import collections
import itertools
import sys
import threading
import time
from queue import PriorityQueue

from termx.terminal import Cursor
from termx.compat import safe_text, PY2, ENCODING

from .utils import get_frames
from .models import HeaderItem, LineItem, SpinnerStates


# TODO: Allow these properties to be configurable
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
INDENT_COUNT = 2


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

        self._groups = []

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
        self._done = False

        self._spinner = None
        self._consumer = None
        self._stdout_lock = lock or threading.Lock()

    @contextlib.contextmanager
    def group(self, text):
        time.sleep(1)
        self.done()

        group = SpinnerGroup(
            text=safe_text(text),
            color=self._color,
            print_interval=self._print_interval,
            interval=self._interval,
            base_indent=self._base_indent + 1,
            lock=self._stdout_lock,
        )
        self._groups.append(group)
        group.start()
        try:
            yield group
        except Exception as e:
            group.error(str(e))
            raise e
        finally:
            group.done()

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
        if not self._done:
            self._done = True
            # Guaranteed to be Change because of OK State
            self._change(state=SpinnerStates.OK, text=text, priority=(1, -2))

            # This will be the highest priority header item, followed by the second
            # highest priority header item which stops the queue consumption.
            # This means that the last header item is guaranteed to print after all
            # lines have been written, and then queue consumption stops.
            # Keeping numbers negative guarantees there is no comparison issue.
            self._put(None, priority=(1, -1))
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

    def write(self, text, state=None, options=None):
        """
        Write a message underneath the last written message waithout changing
        the top level text or spinner.

        Only Updates Header on State Change Associated w/ Line
        """
        state = state or SpinnerStates.NOTSET
        self._change(state)

        line = LineItem(text=text, state=state, options=options)
        self._put(line)

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
            # Note: This will not do anything if the state was already set to
            # ERROR.
            self._change_state(state=SpinnerStates.WARNING)

    def _spin(self):
        while not self._stop_spin.is_set():
            spin_phase = next(self._cycle)
            self._change(frame=spin_phase)

    def _consume(self):
        while True:
            item = self.queue.get()
            if item[1] is None:
                break
            self._update_display(item[1])
            self.queue.task_done()

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
        self._put(header, priority=priority)

        if frame_changed:
            time.sleep(self._interval)

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

    def _put(self, item, priority=None):
        """
        Tuple comparison breaks for equal tuples in Python3, have to use counter
        to ensure no tuples exactly the same.1
        """
        if not priority:
            ct = self.counter[item.type]
            priority = (item.priority, ct)
            self.counter[item.type] += 1
        self.queue.put((priority, item))

    def _update_display(self, item):
        if item.type == 'header':
            self._head_out(item)
        else:
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

        # self._interval = (interval or self._spinner.interval) * 0.001  # Milliseconds to Seconds
        self._interval = (interval or 100) * 0.001  # Milliseconds to Seconds
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
        except Exception as e:
            group.error(str(e))
            raise e
        finally:
            group.done()
