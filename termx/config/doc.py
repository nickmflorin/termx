import copy

from termx.exceptions import (ConfigError, MissingConfigurationError,
    MissingSectionError, ConfigValueError)

from .utils import ConfigDoc


class SectionConfig(ConfigDoc):

    def __init__(self, data):
        self.base_data = copy.deepcopy(data)
        super(SectionConfig, self).__init__(self._section(data))
        self._configure()

    class Meta:
        CONFIG_KEY = None
        NOT_CONFIGURABLE = ()
        ALLOWED = ()

    @classmethod
    def _section(cls, doc):
        config_key = cls._meta('CONFIG_KEY')
        if config_key not in doc:
            raise MissingSectionError(config_key)
        return doc[config_key]

    @classmethod
    def _meta(cls, key):
        return getattr(cls.Meta, key, None)

    def __getattr__(self, attr):
        if not attr.startswith('__'):
            try:
                return self.__getitem__(attr)
            except KeyError:
                section = self._meta('CONFIG_KEY')
                raise MissingConfigurationError(attr, section)
        else:
            return super(SectionConfig, self).__getattr__(attr)

    def _configure(self):
        for key, val in self.items():
            try:
                self._validate_for_configure(key, val)
            except ConfigError as e:
                self._handle_config_error(e)
                del self[key]

        self._backwards_reference_values()

    def override(self, doc):
        """
        After the defaults are loaded and configured on init, overrides are
        applied (optionally) by the user.  We want to add new fields (when
        allowed) and override existing fields (when allowed).
        """
        try:
            section = self._section(doc)
        except ConfigError:
            return
        else:
            for key, val in section.items():
                try:
                    self._validate_for_override(key, val)
                except ConfigError as e:
                    self._handle_config_error(e)
                else:
                    self[key] = val

        self._objectify()


class SimpleSectionConfig(SectionConfig):

    def _backwards_reference_values(self):

        def backwards_ref(val):
            # Check if Referenced by Name in Same Set Already
            if isinstance(val, str) and val in self:
                return self[val]

            # For lists, we want to maintain the parts of the list that cannot
            # be referenced by other values, but also only update the list at
            # the given key if it has any references.
            elif isinstance(val, list):

                list_has_references = False
                for i, element in enumerate(val):
                    if isinstance(element, str) and element in self:
                        list_has_references = True
                        val[i] = self[element]

                # Only Update List if There Were References Changed
                if list_has_references:
                    return val

        updates = []
        for key, val in self.items():
            ref = backwards_ref(val)
            if ref:
                updates.append((key, ref))

        updates = dict(updates)
        self.update(**updates)


class FormatSectionConfig(SimpleSectionConfig):

    # Currently Do Not Have Styles Built In
    REF_MAP = {
        'COLOR': 'COLORS',
        'ICON': 'ICONS',
        'STYLES': 'STYLES',
    }

    def __init__(self, data):
        super(FormatSectionConfig, self).__init__(data)
        self._objectify()

    def _objectify(self):
        from termx.formatting.format import Format
        for key, val in self.items():
            self[key] = Format(
                color=val.get('COLOR'),
                styles=val.get('STYLES', []),
                icon=val.get('ICON')
            )

    def _backwards_reference_values(self):
        """
        In order to solve the problem of self referencing nested fields, i.e.:

        Formats:
            INFO:
                COLOR: BLUE
                ICON:  [!]
            DEBUG: INFO

        what we do is we do not raise an exception during the validation if the
        value is not a dict element.  Instead, we populate the store and then
        validate after the backwards referencing completes that all values
        are dict elements.
        """
        super(FormatSectionConfig, self)._backwards_reference_values()
        for key, val in self.items():
            # All valid non-dict values should have been backwards referenced
            # by now, but we want to throw a different error to inform the user
            # of the invalid value.
            if not isinstance(val, dict):
                continue

            updates = []
            for k, v in val.items():

                ref_doc_name = self.REF_MAP.get(k)
                if ref_doc_name not in self.base_data:
                    raise ConfigError('Colors and Icons must be configured before Formats.')

                ref_doc = self.base_data[ref_doc_name]
                if v in ref_doc:
                    updates.append((k, ref_doc[v]))

            updates = dict(updates)
            val.update(**updates)

        # After Backwards Referencing Done: Validate to make sure that all
        # children are nested/dict structures.
        for key, val in self.items():
            if not isinstance(val, dict):
                raise ConfigValueError(val)


class Colors(SimpleSectionConfig):
    """
    [x] TODO:
    --------
    Rebuild in not allowing the NOT_CONFIGURABLE fields to be overridden
    by the user.  We will have to do this when the configuration is overridden.
    """

    def __init__(self, doc):
        super(Colors, self).__init__(doc)
        self._objectify()

    class Meta:
        CONFIG_KEY = 'COLORS'
        NOT_CONFIGURABLE = ('SHADES', )
        ALLOWED = ()

    def _objectify(self):
        from termx.colorlib.color import color
        for key, val in self.items():
            if isinstance(val, str):
                self[key] = color(val)
            elif isinstance(val, list):
                self[key] = [color(v) for v in val]


class Icons(SimpleSectionConfig):

    class Meta:
        CONFIG_KEY = 'ICONS'
        NOT_CONFIGURABLE = ()
        ALLOWED = ()


class Text(FormatSectionConfig):

    class Meta:
        CONFIG_KEY = 'TEXT'
        ALLOWED = ('COLOR', 'STYLES', 'ICON')
        NOT_CONFIGURABLE = ()


class Formats(FormatSectionConfig):

    class Meta:
        CONFIG_KEY = 'FORMATS'
        ALLOWED = ('COLOR', 'STYLES', 'ICON')
        NOT_CONFIGURABLE = ()
