from ..exceptions import TermxException


class LoggingException(TermxException):
    pass


class InvalidCallable(LoggingException):
    def __init__(self, func, additional=None):
        if hasattr(func, '__name__'):
            self.__message__ = f"The callable {func.__name__} is invalid."
        else:
            self.__message__ = f"The callable {func} is invalid."
        if additional:
            self.__message__ += "\n%s" % additional


class InvalidElement(LoggingException):
    pass
