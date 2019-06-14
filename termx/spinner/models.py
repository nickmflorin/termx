from dataclasses import dataclass, field, InitVar
from datetime import datetime
from enum import Enum
import shutil
import typing

from termx.colorlib import color
from termx.compat import safe_text
from termx.utils import measure_ansi_string
from termx.formatting import Formats, shaded_level


class SpinnerStates(Enum):

    NOTSET = ("Not Set", Formats.State.NOTSET, 0)
    OK = ("Ok", Formats.State.SUCCESS, 1)
    WARNING = ("Warning", Formats.State.WARNING, 2)
    FAIL = ("Failed", Formats.State.FAIL, 3)

    def __init__(self, label, fmt, level):
        self.label = label
        self.fmt = fmt
        self.level = level

    @property
    def icon(self):
        return self.fmt.icon


@dataclass
class LineItemOptions:

    show_icon: bool = True
    label: typing.Union[int, str] = None

    # If color_icon = False, or color_bullet = False, the icon or bullet will be
    # "shaded" based on the indentation level.
    color_bullet: bool = False  # TODO: Allow string or bool, string sets color.
    color_icon: bool = True  # TODO: Allow string or bool, string sets color.
    color_label: bool = False  # TODO: Allow string or bool, string sets color.

    indent: bool = False  # Additional Indent for Line
    show_datetime: bool = True

    # Validate that the length of the bullet is 1 character.
    bullet: typing.Optional[str] = '>'


@dataclass
class LineItem:

    text: str
    type: str = 'line'
    state: SpinnerStates = SpinnerStates.NOTSET
    indent: int = 0
    priority: int = 0  # "Higher" Than Header Items

    options: InitVar[LineItemOptions] = None
    _options: LineItemOptions = field(init=False)

    def __post_init__(self, options):
        options = options or {}
        self._options = LineItemOptions(**options)

    def _indentation(self, base_indent=0):
        from .core import INDENT_COUNT

        indent_count = (self._indent + 1) + base_indent
        num_spaces = indent_count * INDENT_COUNT
        return num_spaces * " "

    @property
    def _indent(self):
        if self._options.indent:
            return self.indent + 1
        return self.indent

    @property
    def _label_shade(self):
        return shaded_level(self._indent, dark_limit=1)

    @property
    def _text_shade(self):
        return shaded_level(self._indent, dark_limit=2)

    @property
    def _bullet_shade(self):
        return shaded_level(self._indent, dark_limit=3)

    @property
    def _icon_shade(self):
        return shaded_level(self._indent, dark_limit=4)

    @property
    def _text(self):
        fmt = shaded_level(self._indent, dark_limit=1)
        return fmt(self.text)

    @property
    def _label(self):
        if self._options.label:
            if type(self._options.label) is bool and self.state != SpinnerStates.NOTSET:
                return self.state.label
            elif type(self._options.label) is str:
                return self._options.label
        return None

    @property
    def _formatted_label(self):
        """
        Color Label = False means that we are not coloring based on the state
        if the state is set, it is still "shaded" for the indentation level.

        [x] TODO:
        --------
        If `color_label` is a string, color based on that color.
        """
        if self._label:
            if self._options.color_label:
                if type(self._options.color_label) is str:
                    color_ = color(self._options.color_label)
                    return color_(self._label)

                if self.state != SpinnerStates.NOTSET:
                    return self.state.fmt.apply_color(self._label)

            return self._label_shade(self._label)

    @property
    def _formatted_text(self):
        """
        [x] TODO:
        --------
        If `color_label` is a string, color based on that color.
        """
        if self._formatted_label:
            return "%s: %s" % (self._formatted_label, self._text)
        return self.text

    @property
    def _bullet(self):
        """
        Determines the bullet to apply to a given non header line based on
        the state of that written line.

        [x] TODO:
        --------
        Add options to format the bullet.
        Validate that the length of the bullet is 1 character.
        If `color_bullet` is a string, color based on that color.
        """
        state_fmt = self.state.fmt.apply_color

        if self._options.show_icon and self.state != SpinnerStates.NOTSET:

            if self._options.color_icon:
                if type(self._options.color_icon) is str:
                    color_ = color(self._options.color_icon)
                    return color_(self.state.icon)
                else:
                    return state_fmt(self.state.icon)
            else:
                return self._icon_shade(self.state.icon)

        elif self._options.bullet:
            # We Do Not Color Bullet for NOTSET Cases
            if self._options.color_bullet and self.state != SpinnerStates.NOTSET:
                if type(self._options.color_bullet) is str:
                    color_ = color(self._options.color_bullet)
                    return color_(self._options.bullet)
                else:
                    return state_fmt(self._options.bullet)
            else:
                return self._bullet_shade(self._options.bullet)

        return ""

    @property
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
        return "%s %s" % (self._bullet, self._formatted_text)

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
        from .core import DATE_FORMAT

        message = self._indentation(base_indent=base_indent) + self._bulleted
        if not self._options.show_datetime:
            return safe_text(message)

        # TODO: Make DATE_FORMAT Configurable, Make FADED Format Configurable
        date_message = Formats.Text.FADED.with_wrapper("[%s]")(
            datetime.now().strftime(DATE_FORMAT)
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
        from .core import INDENT_COUNT

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
        return color(self.color)

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
