from termx.library import get_version
from simple_settings import settings

from .doc import Colors, Icons, Formats, Text, ConfigDoc

"""
[!] IMPORTANT
------------

If we want to make changse to any of ['ICONS', 'COLORS', 'TEXT', 'FORMATS'],
where the changes is objectified (i.e. changing a color with a string will
store an instance of ``color``) and where changes do not remove other values
in the dict, we have to use

>>> config({...})

There is no hook into simple_settings to force the _Config to regeneratee and
update the simple_settings ``settings``.  Updating singular simple values
with the simple_settings module is fine:

>>> from simple_settings import settings
>>> settings.configure({'SIMPLE': 1})

Or reading from the simple_settings module.  But, the following will not work:

>>> from simple_settings import settings
>>> settings.COLORS.GREEN('Test Message')
>>> Test Message (Shaded Green)  # _Config() Initialized on Termx Init

>>> settings.configure({'COLORS': {'GREEN': '#EFEFEF'}})
>>> settings.COLORS.GREEN('Test Message')
>>> AttributeError
"""


class _Config(object):

    CUSTOM_DOCS = ['ICONS', 'COLORS', 'TEXT', 'FORMATS']

    def __init__(self):
        pass

    @classmethod
    def initialize_settings(cls):

        data = settings.as_dict()
        doc = ConfigDoc(data)

        settings.configure(
            COLORS=Colors(doc),
            ICONS=Icons(doc),
            TEXT=Text(doc),
            FORMATS=Formats(doc)
        )

    @classmethod
    def configure(cls, overrides):
        """
        [x] TODO:
        --------
        We need to perform some sort of config validation here.  We should use
        the Cerberus package and define the schema.  This will also work for
        the styling attributes as well.
        """

        data = settings.as_dict()
        doc = ConfigDoc(data)

        raise Exception()

        # TODO: Come up with an override method that will not alter entire
        # dict structures but only non-destructive changes.
        # >>> doc.update(**overrides)
        # >>> settings.configure(**doc)

        for doc_string in cls.CUSTOM_DOCS:
            if doc_string in doc:

                subdoc = getattr(settings, doc_string)
                subdoc.override(doc)
                settings.configure(**{doc_string: subdoc})

                # If we do not do this, the invalid version will be updated
                # in the next block.
                del doc[doc_string]

        # Update the Rest of the Elements
        settings.configure(**doc)

    @classmethod
    def version(cls):
        from termx import __VERSION__
        return get_version(__VERSION__)


# Read the Defaults on Module Load
config = _Config()
config.initialize_settings()
