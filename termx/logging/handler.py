import logging

from termx.colorlib import color
from termx.exceptions import LoggingError


__all__ = ('TermxLogHandlerMixin', 'TermxLogFormatter', )


class TermxLogFormatter(logging.Formatter):

    def __init__(self, format_string=None, **kwargs):
        super(TermxLogFormatter, self).__init__(**kwargs)
        self.format_string = format_string

    def format(self, record):
        return self.format_string(record)


class TermxLogHandlerMixin(object):

    formatter_cls = TermxLogFormatter

    def default(self, record, attr, default=None):
        setattr(record, attr, getattr(record, attr, default))

    def prepare_record(self, record):
        self.default(record, 'color')
        if record.color:
            if isinstance(record.color, (str, int)):
                setattr(record, 'color', color(record.color))
            elif not isinstance(record.color, color):
                raise LoggingError(
                    "The color provided to the logging record must be of type "
                    "str, int or termx.colorlib.color."
                )
            else:
                setattr(record, 'color', record.color)

    def useTermxFormatter(self, format_string=None):
        formatter = self.formatter_cls(format_string=format_string)
        self.setFormatter(formatter)


def TermxHandler(handler_cls=logging.StreamHandler, format_string=None, **kwargs):

    class _TermxHandler(handler_cls, TermxLogHandlerMixin):

        def __init__(self, filter=None, format_string=None, **kwargs):
            super(_TermxHandler, self).__init__(**kwargs)
            self.useTermxFormatter(format_string=format_string)

        def emit(self, record):
            self.prepare_record(record)
            super(_TermxHandler, self).emit(record)

    return _TermxHandler(format_string=format_string, **kwargs)
