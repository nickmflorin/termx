import logging
import warnings

from termx.exceptions import (
    ConfigError, InconfigurableError, MissingConfigurationError,
    MissingSectionError, DisallowedFieldError, ConfigValueError)

from .constants import STRICT_CONFIG
from .utils import ConfigMapping


logger = logging.getLogger('Configuration')


class ConfigDoc(ConfigMapping):
    """
    Dict subclass specifically for configuration that adds flexibility to how
    items are retrieved and stores keys and values by uppercase transformations.
    """

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = self.__valtransform__(value)

    @classmethod
    def _handle_config_error(cls, e):
        if STRICT_CONFIG:
            raise e
        warnings.warn(str(e))
        logger.warn(str(e))

    def _raise_if_disallowed(self, attr, val):
        allowable_fields = self._meta('ALLOWED')
        if len(allowable_fields) != 0:
            for key, _ in val.items():
                if key not in [fld.upper() for fld in allowable_fields]:
                    raise DisallowedFieldError(key)

    def _raise_if_nonconfigurable(self, attr, val):
        non_configurable = self._meta('NOT_CONFIGURABLE')
        if attr in non_configurable:
            raise InconfigurableError(attr)

    def _validate_for_configure(self, attr, val):
        self._raise_if_disallowed(attr, val)

    def _validate_for_override(self, attr, val):
        self._raise_if_disallowed(attr, val)
        self._raise_if_nonconfigurable(attr, val)

    def __valtransform__(self, value):
        if isinstance(value, dict):
            warnings.warn('Should not be seeing raw dict objects in ConfigDoc.')
            return ConfigDoc(value)
        elif isinstance(value, ConfigDoc):
            return value
        else:
            if isinstance(value, str):
                return value.upper()
            elif isinstance(value, int):
                return value
            elif isinstance(value, list):
                return [
                    self.__valtransform__(v)
                    for v in value
                ]
            elif (hasattr(value, '__class__') and value.__class__.__name__ in
                    ('color', 'style', 'highlight', 'Format')):
                return value
            else:
                raise ConfigValueError(value)


class SectionConfig(ConfigDoc):

    def __init__(self, doc):
        super(SectionConfig, self).__init__(self._section(doc))
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
        try:
            return self.__getitem__(attr)
        except KeyError:
            section = self._meta('CONFIG_KEY')
            raise MissingConfigurationError(attr, section)

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
                new_ref_list = []
                list_has_references = False

                for element in val:
                    ref = backwards_ref(element)
                    if ref:
                        list_has_references = True
                        new_ref_list.append(ref)
                    else:
                        new_ref_list.append(element)

                # Only Update List if There Were References Changed
                if list_has_references:
                    return new_ref_list

        updates = []
        for key, val in self.items():
            ref = backwards_ref(val)
            if ref:
                updates.append((key, ref))

        updates = dict(updates)
        self.update(**updates)


class FormatSectionConfig(SimpleSectionConfig):

    def __init__(self, doc, colors, icons):
        """
        [x] TODO:
        --------
        Have to also allow for self referencing styles.
        """
        self._reference = {
            'COLOR': colors,
            'ICON': icons,
            'STYLES': None,
        }
        super(FormatSectionConfig, self).__init__(doc)
        self._objectify()

    def _objectify(self):
        from termx.formatting.format import Format
        for key, val in self.items():
            assert isinstance(val, ConfigDoc)
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
            if not isinstance(val, ConfigDoc):
                continue

            updates = []
            for k, v in val.items():
                if k != 'STYLES':  # Currently Do Not Have Styles Built In
                    ref = self._reference[k]
                    if v in ref.store:
                        updates.append((k, ref.store[v]))

            updates = dict(updates)
            val.update(**updates)

        # After Backwards Referencing Done: Validate to make sure that all
        # children are nested/dict structures.
        for key, val in self.items():
            if not isinstance(val, ConfigDoc):
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
