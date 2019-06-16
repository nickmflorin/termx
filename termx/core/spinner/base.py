import contextlib
import itertools
import time
import threading

from termx.core.terminal import Cursor

from .models import SpinnerStates, HeaderItem
from ._utils import get_frames


class AbstractSpinner(object):

    def __init__(self, color, spinner, options):

        self.options = options

        self._color = color
        self._spinner = spinner
        self._children = []

        # Spinner doesn't really have depth, but we increment off of it for
        # any children.
        self._depth = -1

        self._frames = get_frames(self._spinner)
        self._cycle = itertools.cycle(self._frames)

        self._state = SpinnerStates.NOTSET
        self._parenting = False

    def _add_line(self):
        pass

    def _group(self, text, index, depth, older_siblings, parent, lock=None):
        from .api import SpinnerGroup

        return SpinnerGroup(
            text=text,
            color=self._color,
            spinner=self._spinner,
            options=self.options,
            index=index,
            depth=depth,
            older_siblings=older_siblings,
            parent=parent,
            # lock=lock,
        )

    def _child(self, text):
        """
        The Spinner is the root level element that childrens different spinner
        groups.  Each of these children groups can also have children.
        """
        return self._group(
            text=text,
            index=len(self._children),
            depth=self._depth + 1,
            older_siblings=self._children,
            parent=self,
        )

    def _run_group(self, group):
        group.start()
        try:
            yield group
        except Exception as e:
            group.error(str(e))
            raise e
        finally:
            group.done()


class AbstractGroup(AbstractSpinner):

    def __init__(self, text, color, spinner, options, index, depth, parent, older_siblings,
            lock=None):
        """
        [x] TODO:
        --------
        If we want to make spinner or frames dynamic, we should add
        getters/setters for these properties.  Right now, we only have one
        spinner, so we don't need them.
        """
        AbstractSpinner.__init__(
            self,
            color=color,
            spinner=spinner,
            options=options,
        )

        self._index = index
        self._depth = depth

        self._parent = parent
        self._older_siblings = older_siblings

        # Initialize the Header Line
        self._text = text
        self._frame = None

        self._stop_spin = threading.Event()
        self._write_lock = lock or threading.Lock()

        self._done = False
        self._spin_thread = None

        self.lines = 0

    def _child(self, text):
        """
        [x] TODO:
        --------
        Children of the top level groups, and subsequent children, need to be
        equipped with the lock so that they can also update their animated
        spinners.

        This is only if we want the animated spinning to be nested, otherewise
        we don't need this method in the AbstractGroup class, just the
        AbstractSpinner class.
        """
        return self._group(
            text=text,
            index=len(self._children),
            depth=self._depth + 1,
            older_siblings=self._children,
            parent=self,
            # lock=self._write_lock,
        )

    def _sibling(self, text):
        """
        The Spinner is the root level element that childrens different spinner
        groups off of it.  The base Spinner cannot add a sibling, but the children
        groups can.
        """
        return self._group(
            text=text,
            index=len(self._parent._children),
            depth=self._depth,
            older_siblings=self._parent._children,
            parent=self._parent,
        )

    @classmethod
    def _print_head(cls, text):
        Cursor.overwrite(text, newline=False)
        Cursor.carriage_return()

    def _print(self, text):
        with self._temporary_newline():
            Cursor.overwrite(text, newline=False)
            Cursor.carriage_return()

    def _move_to_newline(self):
        i = 0
        while i < self.lines:
            Cursor.move_down()
            i += 1
        Cursor.newline()

    def _move_to_head(self):
        i = 0
        while i < self.lines:
            Cursor.move_up()
            i += 1

    def _add_line(self):
        self.lines += 1
        if self._parent:
            self._parent._add_line()

    @contextlib.contextmanager
    def _temporary_newline(self):
        """
        Temporarily moves the cursor to a newline and then immediately back to
        the header line to keep animation smooth.
        """
        try:
            self._move_to_newline()
            self._add_line()
            yield self
        finally:
            self._move_to_head()

    def _spin(self):
        while not self._stop_spin.is_set():
            spin_phase = next(self._cycle)
            time.sleep(self.options.spin_interval)
            self._change(frame=spin_phase)

    def _change(self, state=None, text=None, frame=None, priority=None):

        state = state or SpinnerStates.NOTSET

        state_changed = frame_changed = text_changed = False
        if state:
            state_changed = self._change_state(state)
        if frame:
            frame_changed = self._change_frame(frame)
        if text:
            text_changed = self._change_text(text)

        if any((state_changed, text_changed, frame_changed)):
            header = HeaderItem(
                text=self._text,
                state=self._state,
                frame=self._frame,
                color=self._color,
            )
            self._head_out(header)
        return (state_changed, text_changed, frame_changed)

    def _change_text(self, text):
        """
        Changes the text in the header line immediately.
        """
        if text != self._text:
            self._text = text
            return True
        return False

    def _change_frame(self, frame):
        """
        Changes the text in the header line immediately.
        """
        assert frame != self._frame
        self._frame = frame
        return True

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
        if state.level > self._state.level:
            self._state = state
            return True
        return False

    def _line_out(self, line):
        message = line.format(base_indent=self._depth)
        time.sleep(self.options.write_interval)
        with self._write_lock:
            self._print(message)

    def _head_out(self, item):
        """
        Updates the top level header of the spinner group when either the header
        text changes or the spinner phase changes.

        [x] TODO:
        --------
        Wait until last frame to display state of last line.
        """
        output = item.format(base_indent=self._depth)
        with self._write_lock:
            self._print_head(output)
