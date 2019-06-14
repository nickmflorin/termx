from termx.colorlib import color

from .format import Format
from .exceptions import FormatException

"""
All (most) components in this module are temporary and are just being copied
over from the instattack repo.  We need to have a more consistent terminal coloring
scheme between plumbum and termcolor, one that is flexible and can be used
with the Format object.

Best option would be to use plumbum and allow users to pass in color strings,
and try to match based on what's available.  For curses case, we can try to find
the closest cursor color based on rgba evaluation.

[x] TODO:
--------
Make objects in here configurable, based on a global config option that package
users can specify.
"""


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

        NORMAL = Format(Colors.OFF_BLACK)
        EMPHASIS = Format(Colors.HEAVY_BLACK)

        PRIMARY = Format(Colors.LIGHT_BLACK)
        MEDIUM = Format(Colors.NORMAL_GRAY)
        LIGHT = Format(Colors.LIGHT_GRAY)
        EXTRA_LIGHT = Format(Colors.EXTRA_LIGHT_GRAY)

        FADED = Format(Colors.LIGHT_YELLOW)

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

        FAIL = Format(Color.FAIL, icon=Icon.FAIL)
        SUCCESS = Format(Color.SUCCESS, icon=Icon.SUCCESS)
        WARNING = Format(Color.WARNING, icon=Icon.WARNING)
        NOTSET = Format(Color.NOTSET, icon=Icon.NOTSET)

    class Wrapper:

        INDEX = Format(Colors.OFF_BLACK, wrapper="[%s]", format_with_wrapper=False)


def shaded_level(level, bold=False, dark_limit=0, light_limit=None, gradient=1):
    """
    [x] TODO:
    --------
    It is not a good idea right now to use the `gradient` parameter, because the
    discretized shades are not extensive enough to cover a wide range of shades
    when we use that parameter.

    We should come up with an interpolation method that shades between black
    and white depending on a gradient and a certain percentage.
    """
    light_limit = light_limit or 1
    dark_limit = dark_limit or 0
    slc = slice(dark_limit, -1 * light_limit, gradient)
    shades = Colors.SHADES[slc]

    if len(shades) == 0:
        raise FormatException('Invalid shade limits.')

    try:
        return Format(shades[level], bold=bold)
    except IndexError:
        return Format(shades[-1], bold=bold)
