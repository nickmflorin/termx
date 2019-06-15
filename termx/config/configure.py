from enum import Enum


class FormatEnum(Enum):

    def __init__(self, format):
        self._fmt = format

    def __call__(self, text, **kwargs):
        return self._fmt(text)

    def __getattr__(self, name):
        if name != '_fmt':
            return self._fmt.__getattribute__(name)
        return super(FormatEnum, self).__getattr__(name)


def configure():
    """
    [x] TODO:
    --------
    We have to make these objects configurable from a user defined dictionary
    that they can call on the global module when they use it in their package.
    """
    from termx.core.colorlib.colour import color
    from termx.core.formatting.format import Format

    class Colors:

        GREEN = color('#28a745')
        LIGHT_GREEN = color('DarkOliveGreen3')

        RED = color('#dc3545')
        ALT_RED = color('Red1')
        LIGHT_RED = color('IndianRed')

        YELLOW = color('Gold3')
        LIGHT_YELLOW = color('LightYellow3')

        BLUE = color('#007bff')
        DARK_BLUE = color('#336699')
        TURQOISE = color('#17a2b8')
        ALT_BLUE = color('CornflowerBlue')
        ALT_BLUE_2 = color('RoyalBlue1')

        INDIGO = color('#6610f2')
        PURPLE = color('#364652')
        TEAL = color('#20c997')
        ORANGE = color('#EDAE49')
        BROWN = color('#493B2A')

        HEAVY_BLACK = color('#000000')
        OFF_BLACK = color('#151515')
        LIGHT_BLACK = color('#2a2a2a')
        EXTRA_LIGHT_BLACK = color('#3f3f3f')

        DARK_GRAY = color('#545454')
        NORMAL_GRAY = color('#696969')
        LIGHT_GRAY = color('#a8a8a8')
        EXTRA_LIGHT_GRAY = color('#dbdbdb')
        FADED_GRAY = color('#d7d7d7')

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

    class Icons:

        SKULL = "☠"
        CROSS = "✘"
        CHECK = "✔"
        DONE = "\u25A3"
        TACK = "📌"
        GEAR = "⚙️ "
        CROSSING = "🚧"
        NOTSET = ""

    class Formats:

        class Text:

            NORMAL = Format(color=Colors.OFF_BLACK)
            EMPHASIS = Format(color=Colors.HEAVY_BLACK)

            PRIMARY = Format(color=Colors.LIGHT_BLACK)
            MEDIUM = Format(color=Colors.NORMAL_GRAY)
            LIGHT = Format(color=Colors.LIGHT_GRAY)
            EXTRA_LIGHT = Format(color=Colors.EXTRA_LIGHT_GRAY)

            FADED = Format(color=Colors.LIGHT_YELLOW)

        class State:

            class Icon:

                FAIL = Icons.CROSS
                SUCCESS = Icons.CHECK
                WARNING = Icons.CROSS
                NOTSET = Icons.NOTSET

            class Color:

                FAIL = Colors.RED
                SUCCESS = Colors.GREEN
                WARNING = Colors.YELLOW
                NOTSET = Colors.NORMAL_GRAY

            FAIL = Format(color=Color.FAIL, icon=Icon.FAIL)
            SUCCESS = Format(color=Color.SUCCESS, icon=Icon.SUCCESS)
            WARNING = Format(color=Color.WARNING, icon=Icon.WARNING)
            NOTSET = Format(color=Color.NOTSET, icon=Icon.NOTSET)

        class Wrapper:

            INDEX = Format(color=Colors.OFF_BLACK, wrapper="[%s]", format_with_wrapper=False)

    class LoggingIcons:

        CRITICAL = Icons.SKULL
        ERROR = Icons.CROSS
        WARNING = Icons.CROSSING
        INFO = Icons.TACK
        DEBUG = Icons.GEAR

    class LoggingLevels(FormatEnum):
        """
        [x] TODO:
        ---------
        Make the formats of the logging levels configurable for termx.
        """
        CRITICAL = (Formats.State.FAIL.new_with(styles=['bold'], icon=LoggingIcons.CRITICAL), 50)
        ERROR = (Formats.State.FAIL.new_with(icon=LoggingIcons.ERROR), 40)
        WARNING = (Formats.State.WARNING.new_with(icon=LoggingIcons.WARNING), 30)
        INFO = (Format(color=Colors.BLUE, icon=LoggingIcons.INFO), 20)
        DEBUG = (Formats.Text.MEDIUM.new_with(icon=LoggingIcons.DEBUG), 10)

        def __init__(self, format, num):
            FormatEnum.__init__(self, format)
            self.num = num

    class SpinnerStates(Enum):

        NOTSET = ("Not Set", Formats.State.NOTSET, 0)
        OK = ("Ok", Formats.State.SUCCESS, 1)
        WARNING = ("Warning", Formats.State.WARNING, 2)
        FAIL = ("Failed", Formats.State.FAIL, 3)

        def __init__(self, label, fmt, level):
            self.label = label
            self.fmt = fmt
            self.level = level

        @property
        def icon(self):
            return self.fmt.icon

    return {
        'Colors': Colors,
        'Formats': Formats,
        'Icons': Icons,
        'LoggingIcons': LoggingIcons,
        'LoggingLevels': LoggingLevels,
        'SpinnerStates': SpinnerStates,
    }
