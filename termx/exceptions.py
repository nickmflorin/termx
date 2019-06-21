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


class SpinnerError(TermxException):
    pass


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


class ConfigError(TermxException):
    pass


class ConfigValueError(ConfigError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"Invalid configuration value {self.value}."


class InconfigurableError(ConfigError):
    def __init__(self, attr):
        self.attr = attr

    def __str__(self):
        return f"Attribute {self.attr} is not configurable."


class MissingConfigurationError(ConfigError):
    def __init__(self, attr, section=None):
        self.attr = attr
        self.section = section

    def __str__(self):
        if self.section:
            return f"{self.attr} is not in configuration for {self.section.upper()}."
        return f"{self.attr} is not in configuration"


class MissingSectionError(ConfigError):
    def __init__(self, section):
        self.section = section

    def __str__(self):
        return f"Section {self.section} is missing from config."


class DisallowedFieldError(ConfigError):
    def __init__(self, field):
        self.field = field

    def __str__(self):
        return f"The field {self.field} is not allowed."
