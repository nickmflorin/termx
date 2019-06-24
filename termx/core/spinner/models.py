from dataclasses import dataclass, field, InitVar
from datetime import datetime
from enum import Enum
import shutil
import typing

from termx.core.config import settings
from termx.ext.compat import safe_text
from termx.ext.utils import measure_ansi_string
from termx.core.colorlib.color import color as Color

from ._utils import shaded_level


@dataclass
class TerminalOptions:

    spin_interval: float = 100
    write_interval: float = 25

    def __post_init__(self):
        self.spin_interval = self.spin_interval * 0.001
        self.write_interval = self.write_interval * 0.001


class SpinnerStates(Enum):
    """
    [x] TODO:
    --------
    We might want to make the default spinner state labels configurable.
    """
    NOTSET = ("Not Set", settings.COLORS.NOTSET, settings.ICONS.NOTSET, 0)
    OK = ("Ok", settings.COLORS.SUCCESS, settings.ICONS.SUCCESS, 1)
    WARNING = ("Warning", settings.COLORS.WARNING, settings.ICONS.WARNING, 2)
    FAIL = ("Failed", settings.COLORS.FAIL, settings.ICONS.FAIL, 3)

    def __init__(self, label, color, icon, level):
        self.label = label
        self.color = color
        self.icon = icon
        self.level = level


@dataclass
class LineItemStyle:
    """
    If color_icon = False, or color_bullet = False, the icon or bullet will be
    "shaded" based on the depth level.
    """
    depth: int
    state: SpinnerStates
    fatal: bool

    bullet: typing.Optional[str] = '>'
    color_bullet: typing.Union[bool, str] = False

    show_icon: bool = True
    color_icon: typing.Union[bool, str] = True

    label: typing.Union[bool, str] = False
    color_label: typing.Union[bool, str] = False

    indent: bool = False  # Additional Indent for Line
    show_datetime: bool = True

    def shade_label(self, label):
        fmt = shaded_level(self.depth, dark_limit=1)
        return fmt(label)

    def shade_text(self, text):
        fmt = shaded_level(self.depth, dark_limit=3)
        return fmt(text)

    def shade_bullet(self, bullet):
        fmt = shaded_level(self.depth, dark_limit=5)
        return fmt(bullet)

    def shade_icon(self, icon):
        fmt = shaded_level(self.depth, dark_limit=2)
        return fmt(icon)

    @property
    def _icon(self):
        if self.show_icon and self.state != SpinnerStates.NOTSET:
            if self.color_icon and self.fatal:
                if type(self.color_icon) is str:
                    return Color(self.color_icon)(self.state.icon)
                elif isinstance(self.color_icon, Color):
                    return self.color_icon(self.state.icon)
                else:
                    return self.state.color(self.state.icon)
            else:
                return self.shade_icon(self.state.icon)
        return ""

    @property
    def _bullet(self):
        """
        [x] TODO:
        --------
        Add options to format the bullet.
        Validate that the length of the bullet is 1 character.
        """
        if self.bullet:
            # We Do Not Color Bullet for NOTSET Cases
            if self.color_bullet and self.state != SpinnerStates.NOTSET:
                if type(self.color_bullet) is str:
                    return Color(self.color_bullet)(self.bullet)
                else:
                    return self.state.color(self.bullet)
            else:
                return self.shade_bullet(self.bullet)
        return ""

    @property
    def _label(self):
        """
        Color Label = False means that we are not coloring based on the state
        if the state is set, it is still "shaded" for the indentation level.

        [x] TODO:
        --------
        If `color_label` is a string, color based on that color.
        """
        def get_label():
            if type(self.label) is bool:
                if self.label is False:
                    return None
                else:
                    if self.state != SpinnerStates.NOTSET:
                        return self.state.label

            elif type(self.label) is str:
                return self.label

        def color_label(label):
            if self.color_label:
                if type(self.color_label) is str:
                    return Color(self.color_label)(self._label)
                elif isinstance(self.color_label, Color):
                    return self.color_label(self._label)
                elif self.state != SpinnerStates.NOTSET:
                    return self.state.color(label)
            else:
                return self.shade_label(label)

        label = get_label()
        if label:
            return color_label(label)

    @property
    def _text(self):
        text = self.shade_text(self.text)
        if self._label:
            return "%s: %s" % (self._label, text)
        return text

    def bulleted(self, text):
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
        text = self.shade_text(text)
        if self._label:
            text = "%s: %s" % (self._label, text)

        if not self.fatal:
            if self._icon:
                return "%s %s %s" % (self._bullet, self._icon, text)
            return "%s %s" % (self._bullet, text)
        else:
            if self._icon:
                return "%s %s" % (self._icon, text)
            return "%s %s" % (self._bullet, text)


@dataclass
class ItemMixin:

    text: str
    depth: int
    state: SpinnerStates

    def __post_init__(self, *args, **kwargs):
        self.state = self.state or SpinnerStates.NOTSET

    def indentation(self):
        count = self.indentation_count()
        num_spaces = count * constants.INDENT_COUNT

        # This is Only if We Use Trailing Characer Dots...
        if self.depth == 0:
            return num_spaces * " "

        # This character is the three vertical dots that can be used for
        # trailing the indentation level.
        char = "\u22EE"
        char = ""

        return "%s%s" % (char, (num_spaces * " "))


@dataclass
class LineItem(ItemMixin):

    type: str = 'line'
    fatal: bool = False

    options: InitVar[dict] = None
    style: LineItemStyle = field(init=False)

    def __post_init__(self, options):
        super(LineItem, self).__post_init__()

        options = options or {}
        options.update(
            fatal=self.fatal,
            state=self.state,
            depth=self.depth,
        )
        self.style = LineItemStyle(**options)

    def indentation_count(self):
        """
        For any given "depth" in the tree, the header item sits at the leftmost
        post and the line items start an additional indent count in.
        """
        additional_indent = 0
        if self.style.indent:
            additional_indent = 1
        return self.depth + additional_indent + 1

    def format(self):
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
        message = self.indentation() + self.style.bulleted(self.text)
        if not self.style.show_datetime:
            return safe_text(message)

        # TODO: Make DATE_FORMAT Configurable, Make FADED Format Configurable
        date_message = config.Formats.TEXT.FADED.with_wrapper("[%s]")(
            datetime.now().strftime(constants.DATE_FORMAT)
        )
        columns, _ = shutil.get_terminal_size(fallback=(80, 24))
        separated = (" " * (columns - 5 - measure_ansi_string(date_message) -
            measure_ansi_string(message)))

        # This character is the three vertical dots that can be used for
        # trailing the indentation level.
        char = "\u22EE"
        char = ""

        return safe_text("%s%s%s%s" % (char, message, separated, date_message))


@dataclass
class HeaderItem(ItemMixin):

    frame: str
    color: Color
    type: str = 'header'
    state: SpinnerStates

    def indentation_count(self):
        return self.depth

    def format(self):
        """
        We could format the text with the icon and not have to do it in
        two parts, but for spacing concerns, and possible icon_after/icon_before
        values, we will handle separately.
        """
        designator = None
        if self.state == SpinnerStates.NOTSET:
            designator = self.color(self.frame)
        else:
            designator = self.state.color(self.state.icon)

        # Icon Shouldn't Matter - NOTSET Has no icon...
        output = "%s %s" % (designator, self.state.color(self.text))
        return self.indentation() + output
