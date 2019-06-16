import collections

from termx.core.colorlib import color as Color

from .models import TerminalOptions
from .group import SpinnerMixin


# TODO: Maybe add additional spinners, right now we only care about one for
# simplicity.
sp = collections.namedtuple("Spinner", "frames interval")
default_spinner = sp("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏", 80)


class Spinner(SpinnerMixin):

    def __init__(self, color='black', options=None):
        """
        [x] TODO:
        --------
        Might want to incorporate signal handling similarly to how Yaspin does
        it, although it is out of scope for the time being.

        Do we need an overall spinner thread lock along with individual thread
        locks for the groups?
        """
        self.options = TerminalOptions(**(options or {}))
        self._color = Color(color)

        self._groups = []
        self._base_indent = 0

        # Need to allow updating of spinner for all children/sub children if we
        # make this property dynamic/settable.
        self._spinner = default_spinner
