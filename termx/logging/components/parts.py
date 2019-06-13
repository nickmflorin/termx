# -*- coding: utf-8 -*-
from termx.utils import escape_ansi_string
from termx.logging.exceptions import InvalidElement
from .core import Core


__all__ = (
    'Label',
    'Header',
)


class PartCore(Core):

    def __call__(self, record):
        return self.formatted(record)


class Label(PartCore):

    def __init__(self, delimiter=":", **kwargs):
        super(Label, self).__init__(**kwargs)
        self._delimiter = delimiter

    def __call__(self, record):

        # space_after = " " if space_after else ""
        value = super(Label, self).__call__(record)
        if value:
            if self._delimiter:
                return f"{value}{self._delimiter}"
            return f"{value}"
        return ""


class Header(PartCore):

    def __init__(self, char=None, label=None, length=None, color=None):
        super(Header, self).__init__(color=color)
        self._char = char
        self._length = length
        self._label = label

    def __call__(self, record, owner=None):
        """
        [x] TODO:
        --------
        Make discrepancy between using Parts in groups/objects and passing
        in owner vs. using `self` explicitly.  Maybe even stop the concept
        of "ownner" and use "parent" instead.
        """
        line = self.char_line(record)
        formatter = self.format(record)

        # Format Lines Separately of Label?
        if formatter:
            line = formatter(line)

        label = self.label(record)
        if label:
            return "%s %s %s" % (line, label, line)
        return line

    def label(self, record, owner=None):
        if self._label:
            return self._label(record)
        return ""

    def length(self, record, owner=None):
        """
        [x] TODO:
        --------
        Make discrepancy between using Parts in groups/objects and passing
        in owner vs. using `self` explicitly.  Maybe even stop the concept
        of "ownner" and use "parent" instead.
        """
        if self._length:
            return self._length

        if not owner:
            raise InvalidElement(
                "Header must be in a parent group if length not specified.")

        # [x] TODO: We should make this less strict, and maybe find the length based
        # on the longest child, or some sort of optional parameter that specifies
        # how to determine the length.

        # Determine length based on first element of parent.
        string = owner.valid_children(record)[0](record)
        escaped = escape_ansi_string(string)

        line_length = len(escaped)
        label = self.label(record)
        if label:
            line_length = int(0.5 * (line_length - 2 - len(label)))

        return line_length

    def char_line(self, record, owner=None):
        """
        [x] TODO:
        --------
        Make discrepancy between using Parts in groups/objects and passing
        in owner vs. using `self` explicitly.  Maybe even stop the concept
        of "ownner" and use "parent" instead.
        """
        return self._char * self.length(record)
