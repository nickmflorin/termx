import contextlib
import collections

from termx.ext.compat import safe_text

from termx.core.terminal import Cursor
from termx.core.colorlib import color as Color

from .group import SpinnerGroup


# TODO: Maybe add additional spinners, right now we only care about one for
# simplicity.
sp = collections.namedtuple("Spinner", "frames interval")
default_spinner = sp("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏", 80)


class Spinner(object):

    def __init__(self, color='black', interval=None, print_interval=None):
        """
        [x] TODO:
        --------
        Might want to incorporate signal handling similarly to how Yaspin does
        it, although it is out of scope for the time being.

        Do we need an overall spinner thread lock along with individual thread
        locks for the groups?
        """
        self._groups = []
        self._color = Color(color)

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
            spinner=self._spinner,
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
