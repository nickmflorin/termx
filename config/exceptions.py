class ConfigError(Exception):
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
