from termx.library import get_version

from .doc import Colors, Icons, Formats, Text, ConfigDoc
from .utils import read_default_config, ConfigMapping

"""
[x] TODO:
--------
Currently, other modules importing the configurable constants for colors,
formats, etc. would have to do it like:

>>> from termx.configig import config
>>> config.Colors.BLUE

This is not what we want, we want to be able to import Colors, Formats, etc.
directly.

[x] TODO:
--------
Once we move the configuration of colors and formats to the top level module,
this configuration style module is probably not needed anymore, so we can
deprecate.
"""


class _Config(ConfigMapping):

    CUSTOM_DOCS = ['ICONS', 'COLORS', 'TEXT', 'FORMATS']

    @classmethod
    def read(cls):

        doc = read_default_config()
        icons = Icons(doc)
        colors = Colors(doc)

        doc.update({
            'COLORS': colors,
            'ICONS': icons,
            'TEXT': Text(doc, colors=colors, icons=icons),
            'FORMATS': Formats(doc, colors=colors, icons=icons)
        })
        return cls(doc)

    def update(self, doc):
        """
        Only sets the value to the new value if present in the data, otherwise
        maintains the original value.
        """
        for key, val in doc.items():
            if val is not None:
                self[key] = val

    def __call__(self, data):
        """
        [x] TODO:
        --------
        We need to perform some sort of config validation here.  We should use
        the Cerberus package and define the schema.  This will also work for
        the styling attributes as well.
        """
        doc = ConfigDoc(data)

        for doc_string in self.CUSTOM_DOCS:
            if doc_string in doc:
                self[doc_string].override(doc)
                del doc[doc_string]

        # Update the Rest of the Elements
        self.update(doc)

    def version(self):
        from termx import __VERSION__
        return get_version(__VERSION__)


# Read the Defaults on Module Load
config = _Config.read()
