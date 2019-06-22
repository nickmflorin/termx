from simple_settings import settings as Settings

from termx.exceptions import ConfigError

from .doc import ConfigDoc
from .sections import ColorsDoc, IconsDoc, FormatsDoc, TextDoc

"""
[!] IMPORTANT
-------------
This all starts to fall apart if we override a value that was self referenced.
If we have 'PRIMARY' = 'GRAY' and we set 'GRAY' to a different value, it will
not reflect in 'PRIMARY', because 'PRIMARY' was already changed.

Fixing this would require a lot of complexity though, so maybe instead we should
limit self-referencing values like 'PRIMARY'.
"""


class _Config(object):

    CUSTOM_DOCS = ['ICONS', 'COLORS', 'TEXT', 'FORMATS']

    def __init__(self):
        """
        When settings are initially loaded, ICONS, COLORS, TEXT and FORMATS
        sections will all be plain old dict(s).  We want to convert them to
        ConfigDoc instances so we can leverage the overridden dict behavior.

        [x] TODO:
        --------
        This will be reserved for loading the default system settings (defined
        by developer) and not the possible overridden user settings.  This means
        that we don't **have** to validate the settings, but we probably should
        use Cerberus anyways.
        """
        data = Settings.as_dict()
        Settings.configure(
            COLORS=ColorsDoc(data),
            ICONS=IconsDoc(data),
            TEXT=TextDoc(data),
            FORMATS=FormatsDoc(data)
        )

    def __call__(self, *args, **kwargs):
        """
        [x] TODO:
        --------
        We need to perform some sort of config validation here.  We should use
        the Cerberus package and define the schema.  This will also work for
        the styling attributes as well.

        [x] NOTE:
        --------
        We have to access attributes on `Settings` instead of using Settings.as_dict().
        This is because Settings.as_dict() will also call the __dict__ methods
        on ConfigDoc instances, converting them to plain old dicts.
        """
        override = dict(*args, **kwargs)
        for key, val in override.items():
            if key in self.CUSTOM_DOCS:
                if getattr(Settings, key, None) is None:
                    raise ConfigError(f"{key} was never configured!")

                doc = getattr(Settings, key)
                if not isinstance(doc, ConfigDoc):
                    raise ConfigError(f"{key} should have been configured as ConfigDoc!")

                # Non-destructive update
                doc.update(**val)
                Settings.configure(**{key: doc})
            else:
                Settings.configure(**{key: val})


# Read the Defaults on Module Load
# Note that this module is imported whenever simple_settings.settings is imported,
# since all the settings files are nested in this module.
config = _Config()
