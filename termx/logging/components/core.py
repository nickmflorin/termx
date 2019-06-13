# -*- coding: utf-8 -*-
import contextlib

from ...utils import humanize_list, string_format_tuple
from .decoration import Decoration
from .utils import get_format, get_value


__all__ = (
    'SegmentCore',
    'LineCore',
    'LinesCore',
    'LogFormatCore',
)


class Core(object):

    def __init__(self, attrs=None, value=None, fmt=None, color=None):

        self._attrs = attrs
        self._color = color
        self._value = value
        self._format = fmt

    def formatted(self, record):
        value = self.value(record)
        if value:
            format = self.format(record)
            if format:
                try:
                    return format("%s" % value)
                except TypeError:
                    if isinstance(self._value, tuple):
                        value = string_format_tuple(value)
                        return format(value)
                    else:
                        raise
            else:
                return value
        return ""

    def valid(self, record):
        return self.value(record) is not None

    def format(self, record):
        if self._format:
            return get_format(record, self._format)
        elif self._color:
            return get_format(record, self._color)

    def value(self, record):
        if self._attrs or self._value:
            return get_value(record, attrs=self._attrs, value=self._value)
        return ""


class ElementCore(Core):

    def __init__(self, decoration=None, **kwargs):
        super(ElementCore, self).__init__(**kwargs)

        decoration = decoration or {}
        self.decoration = Decoration.from_dict(decoration)

    def decorate(self, data):
        self.decoration.decorate_with(data)


class ParentMixin(object):

    def __init__(self, *children):
        # It is important that we do not copy the mutable list of children
        # for purposes of dynamic children.
        self.children = list(children[:] or [])
        # self.validate_children()

    def valid_children(self, record):
        valid_children = []
        for child in self.children:
            if child.valid(record):
                valid_children.append(child)
        return valid_children

    def valid(self, record):
        return len(self.valid_children(record)) != 0

    @property
    def child_cls(self):
        raise NotImplementedError("Property `child_cls` must be implemented.")

    def validate_children(self):
        """
        We want to allow only the `child_cls` instances, as well as a dynamic
        function that returns a series of objects based on the record.

        This means that we have to test for exclusion instead of inclusion
        of elements.

        [x] TODO:
        --------
        Make this more concrete.
        """
        humanized_children = [
            cls_.__name__ if not isinstance(cls_, str) else cls_
            for cls_ in self.child_cls
        ]
        for child in self.children:
            if child.__class__.__name__ not in humanized_children:
                if not hasattr(child, '__dynamic__'):
                    humanized_children = humanize_list(humanized_children, conjunction='or')
                    raise ValueError(
                        f'All children of {self.__class__.__name__} '
                        f'must be instances of {humanized_children}, not '
                        f'{child.__class__.__name__}.'
                    )

    def decorate_children(self, data):
        for child in self.children:
            if isinstance(child, ParentMixin):
                child.decorate_children(data)
            else:
                child.decorate(data)
        self.decorate(data)


class SegmentCore(ElementCore):
    """
    Each "Segment" is a series of Parts, which form the most basic objects
    of construction.  Segments are used to comprise the different components
    of a "Line".

    For example, a Segment may consist of a Label and a core value:

    Segment = "Label: Value"
    Segment = ["Label", "Value"]
    Segment = [Part, Part]
    """

    def __init__(self, label=None, **kwargs):
        ElementCore.__init__(self, **kwargs)
        self._label = label

    def label(self, record):
        if self._label:
            return self._label(record)
        return ""


class LineCore(ParentMixin, SegmentCore):
    """
    Each "Line" is a series of Segments, where each Segment has a series of Parts,
    which represent the most basic objects of the construction.

    Parts return only a string representation of themselves, and are joined together
    to form a Segment.  For example, a Segment can consist of a Label, a Prefix
    and the core value.  You can have two of those segments forming a line,
    which might be:

    Line = "Label 1: (Error) Value2 Label 2: (Not Error) Value2"
    Line = ["Label 1: (Error) Value2", "Label 2: (Not Error) Value2"]
    Line = [[Part, Part, Part], [Part, Part, Part]]
    Line = [Segment, Segement]
    """
    child_cls = ('Segment', )

    def __init__(self, *children, **kwargs):
        """
        [x] TODO:
        -------
        -  Allow lines above and lines below to be passed in for a Line instance.
        """
        SegmentCore.__init__(self, **kwargs)  # Passes Label Up
        ParentMixin.__init__(self, *children)


class LinesCore(LineCore):

    child_cls = ('Line',)

    def __init__(
        self,
        *children,
        header=None,
        lines_above=0,
        lines_below=0,
        **kwargs,
    ):
        # No Label or Decoration
        LineCore.__init__(self, *children, **kwargs)

        self._header = header

        # We Might Also Want to Apply These to a Line
        # TODO: Add these to decoration...
        self._lines_above = lines_above
        self._lines_below = lines_below

    def header(self, record):
        if self._header:
            return self._header(record)
        return ""

    @contextlib.contextmanager
    def lines_context(self, record):
        lines = [' ' for i in range(self._lines_above)]
        lines += [self.header(record)]
        try:
            yield lines
        finally:
            lines += [' ' for i in range(self._lines_below)]


class LogFormatCore(LinesCore):

    child_cls = ('Line', 'Lines', 'Dynamic',)

    def __init__(self, *children, width=100, **kwargs):
        """
        [x] TODO:
        -------
        -  Make sure all children are instances of `Lines` - we do not have
           support yet for other children.
        -  Add support so that LogFormat can wrap any type of child object.
        -  Allow LogFormat to be passed a header.
        """
        LinesCore.__init__(self, *children, **kwargs)
        self._width = width
