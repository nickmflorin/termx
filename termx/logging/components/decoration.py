# -*- coding: utf-8 -*-
from dataclasses import dataclass
from dacite import from_dict
from typing import Optional
from textwrap import TextWrapper
import os

from termx.utils import measure_ansi_string
from .utils import get_format


@dataclass
class Decorative:
    char: str
    fmt: Optional[object] = None
    color: Optional[object] = None

    def format(self, record):
        if self.fmt:
            return get_format(record, self.fmt)
        elif self.color:
            return get_format(record, self.color)

    @property
    def length(self):
        # Measure ansi string is probably not longer applicable (unless we pass
        # in a formatted prefix or suffix) which this will safeguard.
        return measure_ansi_string(self.char)

    @classmethod
    def from_dict(cls, data):
        return from_dict(data_class=cls, data=data)


@dataclass
class Prefix(Decorative):
    tight: bool = False

    def apply(self, text, record=None):
        prefix = self.char
        if record:
            fmt = self.format(record)
            if fmt:
                prefix = fmt(prefix)

        spacing = " "
        if self.tight:
            spacing = ""
        return "%s%s%s" % (prefix, spacing, text)


@dataclass
class Suffix(Decorative):

    def apply(self, text, record=None):
        suffix = self.char
        if record:
            fmt = self.format(record)
            if fmt:
                suffix = fmt(suffix)

        return "%s%s" % (text, suffix)


@dataclass
class Delimiter(Decorative):

    tight: bool = True

    def apply(self, parts):
        char = self.char
        if not self.tight:
            char = "%s " % self.char
        return char.join(parts)


@dataclass
class Decoration:

    delimiter: Delimiter = Delimiter(char=" ")
    prefix: Optional[Prefix] = None
    suffix: Optional[Suffix] = None
    width: Optional[int] = 0
    indent: Optional[int] = 0

    def join(self, parts):
        return self.delimiter.char.join(parts)

    def apply_to_text(self, text, record=None, prefix=True, suffix=True):
        if self.prefix and prefix:
            text = self.prefix.apply(text, record=record)
        if self.suffix and suffix:
            text = self.suffix.apply(text, record=record)
        return text

    def apply_to_parts(self, parts, record=None, prefix=True, suffix=True):
        text = self.delimiter.apply(parts)
        return self.apply_to_text(text, record=record, prefix=prefix, suffix=suffix)

    def decorate_with(self, data):
        """
        [x] TODO:
        --------
        Right now we just use this for passing the width from the LogFormat
        down through the children, but later we might want to make this more
        flexible for nested objects.
        """
        for key, val in data.items():
            setattr(self, key, val)

    def wrap(self, text, record):
        wrapper = self.wrapper(record)
        return wrapper.wrap(text=text)

    def wrapper(self, record):
        subsequent_indent = initial_indent = self.indentation()
        if self.prefix:
            subsequent_indent = self.indentation(
                additional=self.prefix.length + 1
            )
            indentation = self.indentation()
            initial_indent = self.prefix.apply(indentation, record=record)

        return TextWrapper(
            width=self.wrap_width,
            initial_indent=initial_indent,
            subsequent_indent=subsequent_indent,
        )

    def indentation(self, count=None, additional=0):
        count = count or self.indent or 0
        count += additional
        return count * " "

    @property
    def wrap_width(self):
        if self.width:
            return self.width
        _, columns = os.popen('stty size', 'r').read().split()
        columns = int(columns)
        return columns - 5

    @classmethod
    def from_dict(cls, data):
        formed_data = {}
        formed_data['indent'] = data.get('indent', 0)
        formed_data['width'] = data.get('width', 0)

        if data.get('prefix'):
            prefix = data['prefix']
            if isinstance(prefix, dict):
                formed_data['prefix'] = Prefix.from_dict(prefix)
            else:
                formed_data['prefix'] = Prefix(char=prefix)

        if data.get('suffix'):
            suffix = data['suffix']
            if isinstance(suffix, dict):
                formed_data['suffix'] = Suffix.from_dict(suffix)
            else:
                formed_data['suffix'] = Suffix(char=suffix)

        if data.get('delimiter'):
            delimiter = data['delimiter']
            if isinstance(delimiter, dict):
                formed_data['delimiter'] = Delimiter.from_dict(delimiter)
            else:
                formed_data['delimiter'] = Delimiter(char=delimiter)

        return from_dict(data_class=cls, data=formed_data)
