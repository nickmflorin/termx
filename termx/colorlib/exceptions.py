from termx.exceptions import TermxException


class ColorLibError(TermxException):
    pass


class InvalidColor(ColorLibError):
    def __init__(self, value):
        self.__message__ = f"The color {value} is invalid."


class InvalidStyle(ColorLibError):
    def __init__(self, value):
        self.__message__ = f"The style {value} is invalid."
