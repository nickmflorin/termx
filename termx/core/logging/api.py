from .handler import TermxHandler  # noqa
from .components.parts import Header, Label
from .components.base import SegmentCore, LineCore, LinesCore, LogFormatCore


__all__ = (
    'Label',
    'Header',
    'Segment',
    'Line',
    'Lines',
    'LogFormat',
    'DynamicLines',
    'TermxHandler',
)


def filter_missing(func):
    """
    Filters empty strings from any function returning a list of components.
    """
    def wrapped(instance, record, **kwargs):
        results = func(instance, record, **kwargs)
        filtered = []
        for result in results:
            if result != "":
                filtered.append(result)
        return filtered
    return wrapped


class Segment(SegmentCore):
    """
    Each "Segment" is a series of Parts, which form the most basic objects
    of construction.  Segments are used to comprise the different components
    of a "Line".

    For example, a Segment may consist of a Label and a core value:

    Segment = "Label: Value"
    Segment = ["Label", "Value"]
    Segment = [Part, Part]
    """

    def __call__(self, record):
        """
        Joins the parts of the single segment together to form a single string,
        and then wraps that string around the provided width, indeent and dedent
        of the TextWrapper, returning a list of lines.

        [!] IMPORTANT
        --------------
        If we pass a prefix to a segment this will get messed up, since we do
        not account for it in the indentation or the wrapped prefix.

        [x] TODO
        --------
        Incorporate text wrapping into the decorative data classes so that the
        prefix can be automatically connsumed within the text wrapping process,
        along with the indnentation.
        """
        parts = self.parts(record)
        # We have to add prefix separately when we wrap text - but we do not
        # do that for segments?  See IMPORTANT above.
        line = self.decoration.apply_to_parts(parts, record=record, prefix=False)
        return self.decoration.wrap(line, record)  # List of Lines

    @filter_missing
    def parts(self, record):
        """
        [x] NOTE:
        --------
        We don't want to remove entire segments (or other structures) if just
        some decoration (like a label or prefix) cannot be evaluated/is invalid.

        We only want to not show the segment if the core value is invalid, which
        means we cannot filter out invalid components based on one element
        being missing (after the parts list is created), we have to specifically
        target the core value.
        """
        if self.valid(record):
            return [
                self.label(record),
                self.formatted(record),
            ]
        return []


class Line(LineCore):
    """
    Displays a series of log items each on the same line in the display.

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

    def __call__(self, record):
        """
        [x] TODO
        --------
        Incorporate text wrapping into the decorative data classes so that the
        prefix can be automatically connsumed within the text wrapping process,
        along with the indnentation.
        """
        segments = self.segments(record)
        # We have to add prefix separately when we wrap text.
        line = self.decoration.apply_to_parts(segments, record=record, prefix=False)
        return self.decoration.wrap(line, record)  # Returns Set of Lines

    @filter_missing
    def segments(self, record):
        """
        [x] NOTE:
        --------
        We don't want to remove entire segments (or other structures) if just
        some decoration (like a label or prefix) cannot be evaluated/is invalid.

        We only want to invalidate the entire line if none of the children are
        valid.
        """
        lines = []
        for child in self.valid_children(record):
            child_lines = child(record)
            lines.extend(child_lines)
        return lines


class Lines(LinesCore):
    """
    Displays a series of log items each on a new line in the display.
    """

    def __call__(self, record):

        lines = self.lines(record)

        newlines = []
        for item in lines:
            text = self.decoration.wrap(item, record)
            for element in text:
                newlines.append(element)
        return newlines

    @filter_missing
    def lines(self, record):
        with self.lines_context(record) as lines:
            for child in self.valid_children(record):
                lines.extend(child(record))
        return lines


class DynamicLines(Lines):
    """
    [x] TODO:
    ---------
    Figure out a more elegant way of doing this that could involve wrapping
    a generator in a Dynamic() method, that returns a dynamic class.
    """

    def _dynamic_children(self, record):
        self.children = []  # Very Important
        for child in self.dynamic_children(record):
            self.children.append(child)


class LogFormat(LogFormatCore):

    def __call__(self, record):

        # Have to decorate after we create dynamic elements.
        for i, child in enumerate(self.children):
            if isinstance(child, DynamicLines):
                child._dynamic_children(record)

        self.decorate_children({'width': self._width})

        with self.lines_context(record) as lines:
            for group in self.valid_children(record):
                lines.extend(group(record))
        return "\n" + "\n".join(lines)
