import importlib

from termx.ext import get_version


class _Config(dict):

    constants = importlib.import_module('.constants', package=__name__)

    Colors = None
    Formats = None
    Icons = None
    LoggingLevels = None
    LoggingIcons = None  # TODO: Maybe leave out
    SpinnerStates = None

    def __init__(self, data):
        """
        [x] TODO:
        --------
        We will start having to pass in the user defined data to the configure
        method when they load the module.  How we are going to do this is unclear
        at this point - right now we are just trying to avoid circular imports.
        """
        from .configure import configure

        style_configs = configure()
        for key, val in style_configs.items():
            setattr(self, key, val)

        super(_Config, self).__init__(data)

    def version(self):
        from termx import __VERSION__
        return get_version(__VERSION__)


config = _Config({})
