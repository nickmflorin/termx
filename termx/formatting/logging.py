from enum import Enum
from termx.formatting import Icons, Formats, Format, Colors


__all__ = (
    'LoggingLevels',
    'LoggingIcons',
)


class LoggingIcons:

    CRITICAL = Icons.SKULL
    ERROR = Icons.CROSS
    WARNING = Icons.CROSSING
    INFO = Icons.TACK
    DEBUG = Icons.GEAR


class FormatEnum(Enum):

    def __init__(self, format):
        self._fmt = format

    def __call__(self, text, **kwargs):
        return self._fmt(text)

    def __getattr__(self, name):
        if name != '_fmt':
            return self._fmt.__getattribute__(name)
        return super(FormatEnum, self).__getattr__(name)


class LoggingLevels(FormatEnum):
    """
    [x] TODO:
    ---------
    Make the formats of the logging levels configurable for termx.
    """
    CRITICAL = (Formats.State.FAIL.with_style('bold').with_icon(LoggingIcons.CRITICAL), 50)
    ERROR = (Formats.State.FAIL.with_icon(LoggingIcons.ERROR), 40)
    WARNING = (Formats.State.WARNING.with_icon(LoggingIcons.WARNING), 30)
    INFO = (Format(Colors.BLUE, icon=LoggingIcons.INFO), 20)
    DEBUG = (Formats.Text.MEDIUM.with_icon(LoggingIcons.DEBUG), 10)

    def __init__(self, format, num):
        FormatEnum.__init__(self, format)
        self.num = num
