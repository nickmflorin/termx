import importlib

from termx.ext import get_version


"""
[x] TODO:
--------
Currently, other modules importing the configurable constants for colors,
formats, etc. would have to do it like:

>>> from termx.config import config
>>> config.Colors.BLUE

This is not what we want, we want to be able to import Colors, Formats, etc.
directly.

[x] TODO:
--------
Once we move the configuration of colors and formats to the top level module,
this configuration style module is probably not needed anymore, so we can
deprecate.
"""

global Colors
global Styles
global Formats
global Icons


class _Config(dict):
    from .defaults import __FORMATS__
    constants = importlib.import_module('.constants', package=__name__)
    Formats, Colors, Styles, Icons = __FORMATS__({})

    def __init__(self, data):
        super(_Config, self).__init__(data)

        # These Will be the Defaults
        # self.Formats, self.Colors, self.Styles, self.Icons = __FORMATS__({})

    def __call__(self, data):
        from .defaults import __FORMATS__

        global Colors
        global Styles
        global Formats
        global Icons

        Formats, Colors, Styles, Icons = __FORMATS__(data)
        return Formats, Colors, Styles, Icons
    # @classmethod
    # def configure(cls, data):
    #     print(cls.Colors.GREEN('Configuring Config'))
    #     from .defaults import __FORMATS__
    #     cls.Formats, cls.Colors, cls.Styles, cls.Icons = __FORMATS__(data)
    #     print(cls.Colors.GREEN('Done Configuring Config'))

    def version(self):
        from termx import __VERSION__
        return get_version(__VERSION__)


from .defaults import __FORMATS__

# These Will be the Defaults
config = _Config({})
Formats, Colors, Styles, Icons = __FORMATS__({})


