from copy import deepcopy
import logging
import warnings

from termx.ext.utils import ensure_iterable


logger = logging.getLogger('Configuration')


# Not Sure How to Handle Yet
STRICT = True


class ConfigError(Exception):
    pass


class CannotSetError(ConfigError):
    def __init__(self, attr):
        self.attr = attr

    def __str__(self):
        return "Cannot set attribute %s via configuration." % self.attr


class ConfigurableSet(object):
    """
    An object with static class properties that can be altered at runtime via
    a dictionary containing information for package configuration.
    """
    __CONFIG_KEY__ = None
    __CAN_ADD__ = True  # Can Configuration Add Additional Properties
    __NOT_CONFIGURABLE__ = []

    @classmethod
    def find_configuration(cls, data):
        """
        Finds the relevant configuration in the dataset based on a flexible
        key identification.  This allows users to specify the config for
        an object as:

        >>> {'COLORS': {...}}
        >>> {'Colors': {...}}
        >>> {'colors': {...}}
        >>> ...
        """
        def _find_configuration(data_dict, config_key):
            for key, val in data_dict.items():
                if key.lower() == config_key:
                    return data_dict[key]
            return None

        keys = ensure_iterable(cls.__CONFIG_KEY__, coercion=list, force_coerce=True)
        if len(keys) == 1:
            return _find_configuration(data, keys[0])
        else:
            index = 0
            data_dict = deepcopy(data)
            while index < len(keys):
                data_dict = _find_configuration(data_dict, keys[index])

                if data_dict is None:
                    return None

                # TODO: Add more detailed error description.
                elif not isinstance(data_dict, dict):
                    raise ConfigError('Invalid configuration specified.')

            return data_dict

    @classmethod
    def configure_value(cls, attr, val):
        setattr(cls, attr, val)

    @classmethod
    def configure(cls, data):
        """
        Finds the relevant dictionary in the configuration data supplied
        (if it exists) based on a flexible valued key.  If the configuration
        data is found, applies each data point to the current class by
        setting the attribute on the class equal to the configuration specified
        value (if valid).
        """
        configuration_data = cls.find_configuration(data)
        if not configuration_data:
            return

        for attr, val in configuration_data.items():

            if attr in cls.__NOT_CONFIGURABLE__:
                if STRICT:
                    raise CannotSetError(attr)

                warnings.warn('Attribute %s is not configurable.' % attr)
                logger.warning('Attribute %s is not configurable.' % attr)

            elif not hasattr(cls, attr) and not cls.__CAN_ADD__:
                if STRICT:
                    raise CannotSetError(attr)
                warnings.warn('Attribute %s is not configurable.' % attr)
                logger.warning('Attribute %s is not configurable.' % attr)

            else:
                cls.configure_value(attr, val)


def __ICONS__(data):

    class ICONS(ConfigurableSet):
        __CONFIG_KEY__ = 'icons'

        SKULL = "☠"
        CROSS = "✘"
        CHECK = "✔"
        TACK = "📌"
        GEAR = "⚙️ "
        CROSSING = "🚧"
        NOTSET = ""

        # States
        FAIL = CROSS
        SUCCESS = CHECK
        WARNING = CROSS

        # Logging
        DEBUG = GEAR
        INFO = TACK
        ERROR = CROSS
        CRITICAL = SKULL

        @classmethod
        def configure_value(cls, attr, val):
            """
            [x] TODO:
            --------
            Validate icons for the number of characters.
            """
            super(ICONS, cls).configure_value(attr, val)

    ICONS.configure(data)
    return ICONS


def __STYLES__(data):

    class STYLES:
        __CONFIG_KEY__ = 'styles'

        @classmethod
        def configure(cls, data):
            """
            [x] TODO:
            --------
            Create a configurable styles object.
            """
            pass

    STYLES.configure(data)
    return STYLES


def __COLORS__(data):

    from termx.core.colorlib.colour import color
    from termx.core.exceptions import InvalidColor

    class COLORS(ConfigurableSet):
        """
        [x] TODO:
        --------
        Standardize colors a little bit more so that the colors a user can override
        are more traditional.

        Allow users to add additional colors to the schematic and access them at
        a later point.

        Change all of our custom Plumbum defined names to HEX Codes.

        Allow the terminal resolution and other terminal aspects to be configurable
        as well.  Things like ANSII codes or maybe curses functionality, etc.

        Figure out how to convert HEX colors to ANSII codes as well.
        """
        __CONFIG_KEY__ = 'colors'
        __NOT_CONFIGURABLE__ = ['SHADES', 'SHADE_NAMES']

        GREEN = color('#28A745')
        LIGHT_GREEN = color('DarkOliveGreen3')

        RED = color('#DC3545')
        ALT_RED = color('Red1')
        LIGHT_RED = color('IndianRed')

        YELLOW = color('Gold3')
        LIGHT_YELLOW = color('LightYellow3')

        BLUE = color('#007bff')
        DARK_BLUE = color('#336699')
        CORNFLOWER_BLUE = color('CornflowerBlue')
        ROYAL_BLUE = color('RoyalBlue1')
        TURQOISE = color('#17a2b8')

        INDIGO = color('#6610f2')
        PURPLE = color('#364652')
        TEAL = color('#20c997')
        ORANGE = color('#EDAE49')
        BROWN = color('#493B2A')

        HEAVY_BLACK = color('#000000')
        OFF_BLACK = color('#151515')
        LIGHT_BLACK = color('#2A2A2A')
        EXTRA_LIGHT_BLACK = color('#3F3F3F')

        DARK_GRAY = color('#545454')
        NORMAL_GRAY = color('#696969')
        LIGHT_GRAY = color('#A8A8A8')
        EXTRA_LIGHT_GRAY = color('#DBDBDB')
        FADED_GRAY = color('#D7D7D7')

        # States: TODO - Allow configuration to specify values that are already
        # set, so you can do something like:
        # >>> configure({'FAIL': 'LIGHT_RED'})
        FAIL = RED
        SUCCESS = GREEN
        WARNING = YELLOW
        NOTSET = NORMAL_GRAY

        # Logging States (WARNING Already Covered)
        CRITICAL = RED
        ERROR = RED
        INFO = BLUE
        DEBUG = NORMAL_GRAY

        # Not Configurable
        SHADES = [
            HEAVY_BLACK,
            OFF_BLACK,
            LIGHT_BLACK,
            EXTRA_LIGHT_BLACK,
            DARK_GRAY,
            NORMAL_GRAY,
            LIGHT_GRAY,
            EXTRA_LIGHT_GRAY,
            FADED_GRAY,
        ]

        # Not Configurable
        SHADE_NAMES = [
            'HEAVY_BLACK',
            'OFF_BLACK',
            'LIGHT_BLACK',
            'EXTRA_LIGHT_BLACK',
            'DARK_GRAY',
            'NORMAL_GRAY',
            'LIGHT_GRAY',
            'EXTRA_LIGHT_GRAY',
            'FADED_GRAY',
        ]

        @classmethod
        def configure_value(cls, attr, val):
            """
            Overrides the default class attribute `attr` value with the provided
            value `val`.

            The attributes can be specified as strings, color instances,
            or HEX codes.

            [x] TODO:
            ---------
            We should expand how they can be configured, and also allow things
            like RGB, ANSII Codes, etc.  This is all handled in the initialization
            method of the `color` object.
            """
            try:
                setattr(cls, attr, color(val))
            except InvalidColor as e:
                if STRICT:
                    raise e
                warnings.warn('The value %s for color %s is invalid.' % (val, attr))
                logger.warn('The value %s for color %s is invalid.' % (val, attr))
            else:
                logger.debug('Configured %s' % attr)

    COLORS.configure(data)
    return COLORS


def __FORMATS__(data):
    """
    [x] TODO:
    --------
    Do we want to make __FORMATS__ configurable?  Or just base them off of the
    formatted __STYLES__ and __COLORS__?
    """
    from termx.core.formatting.format import Format

    Icons = __ICONS__(data)
    Colors = __COLORS__(data)
    Styles = __STYLES__(data)

    class FORMATS(ConfigurableSet):

        __CONFIG_KEY__ = 'formats'

        CRITICAL = Format(color=Colors.CRITICAL, icon=Icons.CRITICAL, styles=['bold'])
        FAIL = Format(color=Colors.FAIL, icon=Icons.FAIL)
        SUCCESS = Format(color=Colors.SUCCESS, icon=Icons.SUCCESS)
        WARNING = Format(color=Colors.WARNING, icon=Icons.WARNING)
        INFO = Format(color=Colors.INFO, icon=Icons.INFO)
        DEBUG = Format(color=Colors.DEBUG, icon=Icons.DEBUG)
        NOTSET = Format(color=Colors.NOTSET, icon=Icons.NOTSET)

        class TEXT(ConfigurableSet):
            """
            [!] IMPORTANT:
            -------------
            These are probably not necessary anymore.
            Should deprecate?
            """
            __CONFIG_KEY__ = ('formats', 'text')

            NORMAL = Format(color=Colors.OFF_BLACK)
            EMPHASIS = Format(color=Colors.HEAVY_BLACK)

            PRIMARY = Format(color=Colors.LIGHT_BLACK)
            MEDIUM = Format(color=Colors.NORMAL_GRAY)
            LIGHT = Format(color=Colors.LIGHT_GRAY)
            EXTRA_LIGHT = Format(color=Colors.EXTRA_LIGHT_GRAY)

            FADED = Format(color=Colors.LIGHT_YELLOW)

            @classmethod
            def configure_value(cls, attr, val):
                """
                [x] TODO:
                --------
                If we keep this, we should expand on what the user can provide
                to configure (i.e. a dict, maybe a color or a style).

                Also, we should clean up configuration errors particularly for
                these nested objects and make them more verbose.
                """
                if not isinstance(val, Format):
                    raise ConfigError('Must provide an instance of `Format`.')
                setattr(cls, attr, val)

        @classmethod
        def configure(cls, data):
            """
            [x] TODO:
            --------
            Configure FORMATS and deprecate things that we shouldn't use.
            """
            super(FORMATS, cls).configure(data)
            cls.TEXT.configure(data)

        @classmethod
        def configure_value(cls, attr, val):
            """
            [x] TODO:
            --------
            If we keep this, we should expand on what the user can provide
            to configure (i.e. a dict, maybe a color or a style).
            """
            if not isinstance(val, Format):
                raise ConfigError('Must provide an instance of `Format`.')
            setattr(cls, attr, val)

    FORMATS.configure(data)
    return FORMATS, Colors, Styles, Icons
