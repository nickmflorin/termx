from termx.exceptions import TermxException


class FormatException(TermxException):
    pass


class InvalidFormat(FormatException):
    def __init__(self, value):
        self.__message__ = f"The format {value} is invalid."


class InvalidColor(FormatException):
    def __init__(self, value):
        self.__message__ = f"The color {value} is invalid."
