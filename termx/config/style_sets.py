import logging
import warnings

from termx.exceptions import ConfigError, CannotSetError, InvalidColor
from termx.formatting.format import Format
from termx.colorlib import color


logger = logging.getLogger('Configuration')


# Not Sure How to Handle Yet
STRICT = True  # Not Sure How to Handle Yet


class ConfigurableSet(object):
    """
    An object with static class properties that can be altered at runtime via
    a dictionary containing information for package configuration.
    """
    @classmethod
    def get_from_meta(cls, key):
        return getattr(cls.Meta, key, None)

    @classmethod
    def check_if_configurable(cls, attr, value):
        non_configurable = cls.get_from_meta('NOT_CONFIGURABLE')
        if non_configurable:
            non_configurable = [x.upper() for x in non_configurable]
            if attr.upper() in non_configurable:
                raise CannotSetError(attr)

    @classmethod
    def check_if_addable(cls, attr, value):
        can_add = cls.get_from_meta('CAN_ADD')
        if not hasattr(cls, attr) and not can_add:
            raise CannotSetError(attr)

    @classmethod
    def validate_config_value(cls, attr, value):
        cls.check_if_addable(attr, value)
        cls.check_if_configurable(attr, value)

    @classmethod
    def set_configured_value(cls, attr, val):
        setattr(cls, attr.upper(), val)

    @classmethod
    def configure_value(cls, attr, val):
        try:
            cls.validate_config_value(attr, val)
        except ConfigError as e:
            if STRICT:
                raise e

            warnings.warn(str(e))
            logger.warn(str(e))
        else:
            cls.set_configured_value(attr, val)

    @classmethod
    def find_config_data(cls, data):
        config_key = cls.get_from_meta('CONFIG_KEY')
        alterations = [config_key.upper(), config_key.lower(), config_key]

        index = 0
        while index < len(alterations):
            conf = data.get(alterations[index])
            if conf:
                return conf
            index += 1
        return None

    @classmethod
    def configure(cls, data):
        configuration_data = cls.find_config_data(data)
        if not configuration_data:
            return

        for attr, val in configuration_data.items():
            cls.configure_value(attr, val)


def STYLE_CONFIG(data, **kwargs):
    """
    [x] TODO:
    --------
    Do we want to make __FORMATS__ configurable?  Or just base them off of the
    formatted __STYLES__ and __COLORS__?

    If we keep this, we should expand on what the user can provide to configure
    (i.e. a dict, maybe a color or a style).
    """
    class _Icons(ConfigurableSet):

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

        class Meta:
            NOT_CONFIGURABLE = []
            CAN_ADD = True  # Can Add Colors to ICONS Map
            CONFIG_KEY = 'ICONS'

        @classmethod
        def configure_value(cls, attr, val):
            """
            [x] TODO:
            --------
            Validate icons for the number of characters.
            """
            super(_Icons, cls).configure_value(attr, val)

    class _Styles:

        class Meta:
            NOT_CONFIGURABLE = []
            CAN_ADD = True  # Can Add Colors to STYLES Map
            CONFIG_KEY = 'STYLES'

        @classmethod
        def configure(cls, data):
            pass

    class _Colors(ConfigurableSet):
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
        class Meta:
            NOT_CONFIGURABLE = ['SHADES', 'SHADE_NAMES']
            CAN_ADD = True  # Can Add Colors to Color Map
            CONFIG_KEY = 'COLORS'

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

        PURPLE = color('#364652')
        ORANGE = color('#EDAE49')

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
        def set_configured_value(cls, attr, val):
            setattr(cls, attr.upper(), val)

        @classmethod
        def validate_config_value(cls, attr, val):
            """
            [x] TODO:
            ---------
            We should expand how they can be configured, and also allow things
            like RGB, ANSII Codes, etc.  This is all handled in the initialization
            method of the `color` object.
            """
            super(_Colors, cls).validate_config_value(attr, val)
            try:
                color(val)
            except InvalidColor as e:
                raise ConfigError(str(e))

    # Maintain Persistence for Multiple Configure Runs
    Icons = kwargs.get('Icons') or _Icons
    Icons.configure(data)

    # Maintain Persistence for Multiple Configure Runs
    Colors = kwargs.get('Colors') or _Colors
    Colors.configure(data)

    # Maintain Persistence for Multiple Configure Runs
    Styles = kwargs.get('Styles') or _Styles
    Styles.configure(data)

    class _Formats(ConfigurableSet):

        CRITICAL = Format(color=Colors.CRITICAL, icon=Icons.CRITICAL, styles=['bold'])
        FAIL = Format(color=Colors.FAIL, icon=Icons.FAIL)
        ERROR = Format(color=Colors.ERROR, icon=Icons.ERROR)
        SUCCESS = Format(color=Colors.SUCCESS, icon=Icons.SUCCESS)
        WARNING = Format(color=Colors.WARNING, icon=Icons.WARNING)
        INFO = Format(color=Colors.INFO, icon=Icons.INFO)
        DEBUG = Format(color=Colors.DEBUG, icon=Icons.DEBUG)
        NOTSET = Format(color=Colors.NOTSET, icon=Icons.NOTSET)

        class Meta:
            NOT_CONFIGURABLE = []
            CAN_ADD = True  # Can Add Colors to FORMATS Map
            CONFIG_KEY = 'FORMATS'

        @classmethod
        def validate_config_value(cls, attr, val):
            if not isinstance(val, Format):
                raise ConfigError('Must provide an instance of `Format`.')

    class _Text(ConfigurableSet):
        """
        [!] IMPORTANT:
        -------------
        These are probably not necessary anymore.
        Should deprecate?
        """
        NORMAL = Format(color=Colors.OFF_BLACK)
        EMPHASIS = Format(color=Colors.HEAVY_BLACK)

        PRIMARY = Format(color=Colors.LIGHT_BLACK)
        MEDIUM = Format(color=Colors.NORMAL_GRAY)
        LIGHT = Format(color=Colors.LIGHT_GRAY)
        EXTRA_LIGHT = Format(color=Colors.EXTRA_LIGHT_GRAY)

        FADED = Format(color=Colors.LIGHT_YELLOW)

        class Meta:
            NOT_CONFIGURABLE = []
            CAN_ADD = True  # Can Add Colors to TEXT Map
            CONFIG_KEY = 'TEXT'

        @classmethod
        def validate_config_value(cls, attr, val):
            super(_Text, cls).validate_config_value(attr, val)
            if not isinstance(val, Format):
                raise ConfigError('Must provide an instance of `Format`.')

    # Maintain Persistence for Multiple Configure Runs
    Text = kwargs.get('Text') or _Text
    Text.configure(data)

    # Maintain Persistence for Multiple Configure Runs
    Formats = kwargs.get('Formats') or _Formats
    Formats.configure(data)

    return Formats, Text, Colors, Styles, Icons
