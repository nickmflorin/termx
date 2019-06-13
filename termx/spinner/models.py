from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import functools
import shutil

# TODO: Remove dependencies
from instattack.config import constants

from ..compat import safe_text
from ..utils import measure_ansi_string

# TODO: More consistent color setting scheme with project.
from .termcolor import colored
from .constants import INDENT_COUNT
from .utils import get_color


class SpinnerStates(Enum):

    NOTSET = ("Not Set", constants.Formats.State.NOTSET, 0)
    OK = ("Ok", constants.Formats.State.SUCCESS, 1)
    WARNING = ("Warning", constants.Formats.State.WARNING, 2)
    FAIL = ("Failed", constants.Formats.State.FAIL, 3)

    def __init__(self, desc, fmt, level):
        self.desc = desc
        self.fmt = fmt
        self.level = level


@dataclass
class LineItem:

    text: str
    type: str = 'line'
    state: SpinnerStates = SpinnerStates.NOTSET
    indent: int = 0
    priority: int = 0  # "Higher" Than Header Items

    def _indentation(self, base_indent=0):
        indent_count = (self.indent + 1) + base_indent
        num_spaces = indent_count * INDENT_COUNT
        return num_spaces * " "

    def _bullet(self):
        """
        Determines the bullet to apply to a given non header line based on
        the state of that written line.
        """
        if self.state == SpinnerStates.NOTSET:
            pointer_color = constants.Formats.Pointer.get_hierarchal_format(self.indent)
            return pointer_color(">")
        else:
            return self.state.fmt.without_icon()(self.state.fmt.icon)

    def _bulleted(self):
        """
        Only applicable for non-header lines (lines that are not the first in
        the group), where we apply a "bullet" which is either ">" when the state
        is notset for that line or a state icon when the line has a state:

        >>> ✔_Preparing        =========>  Header Line
        >>> __>_First Message   =========>  No State, Bullet = ">"
        >>> ____✘_Something Happened ====>  State, Bullet = ✘

        Returns the unindented form, i.e.

        >>> >_First Message
        >>> ✘_Something Happened

        [x] NOTE:
        --------
        We only want to style the pointer based on the state, and style the
        text based on the hierarchy.
        """
        text_format = constants.Formats.Text.get_hierarchal_format(self.indent)
        return "%s %s" % (self._bullet(), text_format(self.text))

    def format(self, base_indent=0):
        """
        By default, aftere indentation, the writing for each line technically
        starts after (2) spaces; one empty space reserved for an icon or frame
        and the next reserved to separate the icon or frame from the text.

        >>> ✔_Preparing
        >>> __>_First Message
        >>> __✘_Something Happened

        The `indent` refers to a single incremented value, i.e. 0, 1, 2, 3...,
        where each indent value is multiplied times a string setting specifying
        the length of the indent.

        >>> ✔_Preparing        =========>  indent = 0, indentation = indent * SPACE = 0
        >>> __>_First Message   =========>  indent = 1, indentation = indent * SPACE = 2
        >>> ____✘_Something Happened ====>  indent = 2, indentation = indent * SPACE = 4

        (Empty spaces denoted with "_")
        """
        message = self._indentation(base_indent=base_indent) + self._bulleted()

        date_message = constants.Formats.Text.FADED.with_wrapper("[%s]")(
            datetime.now().strftime(constants.DATE_FORMAT)
        )

        columns, _ = shutil.get_terminal_size(fallback=(80, 24))
        separated = (" " * (columns - 5 - measure_ansi_string(date_message) -
            measure_ansi_string(message)))

        return safe_text("%s%s%s" % (message, separated, date_message))


@dataclass
class HeaderItem:

    frame: str
    text: str
    color: str
    type: str = 'header'
    line_index: int = 0
    state: SpinnerStates = SpinnerStates.NOTSET
    indent: int = 0
    priority: int = 1  # "Lower" Than Line Items

    def _indentation(self, base_indent=0):
        num_spaces = (base_indent + self.indent) * INDENT_COUNT
        return num_spaces * " "

    @property
    def color_func(self):
        """
        [x] TODO:
        --------
        Replace with more consistent color formatting scheme, one consistent
        with artsylogger or change artsylogger to use more consistent color
        scheme.
        """
        color = get_color(self.color)
        return functools.partial(colored, color=color)

    def format(self, base_indent=0):
        designator = None
        if self.state == SpinnerStates.NOTSET:
            designator = self.color_func(self.frame)
        else:
            # We could format the text with the icon and not have to do it in
            # two parts, but for spacing concerns, and possible icon_after/icon_before
            # values, we will handle separately.
            designator = self.state.fmt.icon
            designator = self.state.fmt.without_icon()(designator)

        # Icon Shouldn't Matter - NOTSET Has no icon...
        output = "%s %s" % (designator, self.state.fmt.without_icon()(self.text))
        return self._indentation(base_indent=base_indent) + output
