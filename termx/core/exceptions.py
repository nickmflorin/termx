class TermxException(Exception):

    def __init__(self, *args):
        if len(args) == 1:
            self.__message__ = args[0]

    def __str__(self):
        return self.__message__


class FormatError(TermxException):
    pass


class InvalidFormat(FormatError):
    def __init__(self, value):
        self.__message__ = f"The format {value} is invalid."


class ColorLibError(TermxException):
    pass


class InvalidColor(ColorLibError):
    def __init__(self, value):
        self.__message__ = f"The color {value} is invalid."


class InvalidStyle(ColorLibError):
    def __init__(self, value):
        self.__message__ = f"The style {value} is invalid."


class LoggingError(TermxException):
    pass


class InvalidCallable(LoggingError):
    def __init__(self, func, additional=None):
        if hasattr(func, '__name__'):
            self.__message__ = f"The callable {func.__name__} is invalid."
        else:
            self.__message__ = f"The callable {func} is invalid."
        if additional:
            self.__message__ += "\n%s" % additional


class InvalidElement(LoggingError):
    pass
