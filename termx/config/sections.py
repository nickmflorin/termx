import copy

from .exceptions import (ConfigError, MissingConfigurationError,
    MissingSectionError, ConfigValueError, DisallowedFieldError)
from .doc import ConfigDoc


class SectionDoc(ConfigDoc):

    def __init__(self, data):
        self.base_data = data

        # Have to apply the forward referencing before we initialize, otherwise
        # invalid values can be raised on __valtransform__.
        section_data = self.get_section(data)
        forward_referenced_data = self.forward_reference_data(section_data)
        super(SectionDoc, self).__init__(forward_referenced_data)

    @property
    def section_key(self):
        return self._meta('CONFIG_KEY')

    def get_section(self, data):
        if self.section_key not in data:
            raise MissingSectionError(self.section_key)
        return data[self.section_key]

    @classmethod
    def _meta(cls, key):
        return getattr(cls.Meta, key, None)

    def __getattr__(self, attr):
        if not attr.startswith('__'):
            try:
                return self.__getitem__(attr)
            except KeyError:
                raise MissingConfigurationError(attr, self.section_key)
        else:
            return super(SectionDoc, self).__getattr__(attr)

    @classmethod
    def forward_reference_value(cls, data, value):
        if isinstance(value, str):
            if value in data:
                return data[value]

        elif isinstance(value, list):
            if any([v in data for v in value]):
                forward_ref_list = []
                for v in value:

                    # Allow Recursion of Lists
                    ref_val = cls.forward_reference_value(data, v)
                    if ref_val:
                        forward_ref_list.append(ref_val)
                    else:
                        forward_ref_list.append(v)
                return forward_ref_list

        elif isinstance(value, dict):
            if any([v in data for _, v in value.items()]):
                forward_ref_dict = {}
                for k, v in value.items():

                    # Allow Recursion of Dicts
                    ref_val = cls.forward_ref__value(data, v)
                    if ref_val:
                        forward_ref_dict[k] = ref_val
                    else:
                        forward_ref_dict[k] = v
                return forward_ref_dict

        else:
            # Don't Raise Error, Could be Int or Some Non Dict Key Type
            return None

    @classmethod
    def forward_reference_data(cls, data):

        forward_referenced_data = {}
        for k, v in data.items():
            forward_ref = cls.forward_reference_value(data, v)
            if forward_ref:
                forward_referenced_data[k] = forward_ref
            else:
                forward_referenced_data[k] = v
        return forward_referenced_data


class FormatSectionDoc(SectionDoc):

    # Currently Do Not Have Styles Built In
    REF_MAP = {
        'COLOR': 'COLORS',
        'ICON': 'ICONS',
        'STYLES': 'STYLES',
    }

    def __init__(self, data):
        """
        Overridden because we have to apply the forward reference method with
        the original overall data.
        """
        self.base_data = data

        # Have to apply the forward referencing before we initialize, otherwise
        # invalid values can be raised on __valtransform__.
        section_data = self.get_section(data)
        forward_referenced_data = self.forward_reference_data(section_data, data)

        # Note that we don't want to initialize with SectionDoc's __init__ method,
        # but it's parent.
        super(SectionDoc, self).__init__(forward_referenced_data)

    @property
    def allowable_fields(self):
        fields = self._meta('ALLOWED')
        return [fld.upper() for fld in fields]

    def _raise_if_has_disallowed_field(self, val):
        """
        Raises an exception if a certain field is specified for a specific
        object in a ConfigDoc instance that is not allowed.

        Important:  If ALLOWED is empty, that means we do not enforce any fields.

        An example would be a ConfigDoc instance for Format objects, where
        each object is only allowed to have fields (COLOR, STYLE, ICON).
        """
        allowable_fields = self.allowable_fields
        if len(allowable_fields) != 0:
            for key, _ in val.items():
                if key not in [fld.upper() for fld in allowable_fields]:
                    raise DisallowedFieldError(key)

    def __deepcopy__(self, memo):
        """
        Required for simple_settings module.

        In order to maintain custom ConfigDoc dicts with termx objects as
        values (i.e. color, style, Format, etc.) we need to establish a
        __deepcopy__ method for each sub-doc (Colors, Formats, etc.) that
        copies these objects manually.

        For the Format object, it is simple since we already have that
        method built in for purposes of temporary overrides.
        """
        raw = {}
        for key, fmt in self.items():
            raw[key] = fmt.copy()
        return raw

    def __valtransform__(self, value):
        """
        Validates the attribute to ensure that it not a non-configurable param
        before **updating**.
        """
        from termx.fmt import Format

        # Should Only be Case on Initialization (Ideally) - This means this check
        # might be minorly unnecessary.  However, we still want to allow users
        # to update with a dictionary of Format fields.
        if isinstance(value, dict):
            # Error Caught & Handled in __setitem__ Method
            self._raise_if_has_disallowed_field(value)
            return Format(
                color=value.get('COLOR'),
                styles=value.get('STYLES'),
                icon=value.get('ICON'),
                style=value.get('STYLE'),
                wrapper=value.get('WRAPPER'),
                # Depth Required to Avoid Circular Import
                depth=self.base_data['COLOR_DEPTH']
            )
        elif isinstance(value, Format):
            return value
        else:
            raise ConfigValueError(value)

    @classmethod
    def forward_reference_data(cls, data, base_data):
        """
        Almost the same thing as the parent method, but we have to worry about
        the data that could be forward referenced from other docs (i.e. IconsDoc,
        ColorsDoc, StylesDoc).

        Formats:
            INFO:
                COLOR: BLUE
                ICON:  [!]
            DEBUG: INFO

        [x] TODO:
        --------
        -  Add recursion so that nested forward referenced values still work.
        -  There might be a way to more simply refactor this logic with the logic
           in the parent method.
        """
        simple_forward_referenced_data = super(FormatSectionDoc, cls).forward_reference_data(data)

        forward_referenced_data = {}
        for key, value in simple_forward_referenced_data.items():
            if isinstance(value, dict):

                sub_ref = {}  # TODO: Add Recursion Here
                for k, v in value.items():

                    ref_doc_name = cls.REF_MAP.get(k)
                    if ref_doc_name:
                        if ref_doc_name not in base_data:
                            raise ConfigError('Colors and Icons must be configured before Formats.')

                        ref_doc = base_data[ref_doc_name]
                        forward_referenced_value = cls.forward_reference_value(ref_doc, v)
                        if forward_referenced_value:
                            sub_ref[k] = forward_referenced_value
                        else:
                            sub_ref[k] = v

                    else:
                        sub_ref[key] = value

                # This will only work for single nesting until recursion
                # added.
                forward_referenced_data[key] = sub_ref

            else:
                forward_referenced_data[key] = value

        return forward_referenced_data


class ColorsDoc(SectionDoc):
    """
    [x] TODO:
    --------
    Rebuild in not allowing the NOT_CONFIGURABLE fields to be overridden
    by the user.  We will have to do this when the configuration is overridden.
    """
    class Meta:
        CONFIG_KEY = 'COLORS'
        NOT_CONFIGURABLE = ('SHADES', )

    def _copy_val(self, value):
        """
        [!] IMPORTANT:
        --------------
        Before we initialize the settings with the ConfigDoc instances,
        settings.as_dict() is called which will perform a deepcopy
        of the read raw settings.  This means we have to allow the
        copying of str instances.
        """
        if hasattr(value, '__class__') and value.__class__.__name__ == 'color':
            return value.copy()
        elif isinstance(value, list):
            return [self._copy_val(v) for v in value]
        else:
            # Have to Allow Raw Values
            return copy.deepcopy(value)

    def __deepcopy__(self, memo):
        """
        Required for simple_settings module.

        In order to maintain custom ConfigDoc dicts with termx objects as
        values (i.e. color, style, Format, etc.) we need to establish a
        __deepcopy__ method for each sub-doc (Colors, Formats, etc.) that
        copies these objects manually.

        [!] IMPORTANT:
        --------------
        Before we initialize the settings with the ConfigDoc instances,
        settings.as_dict() is called which will perform a deepcopy
        of the read raw settings.  This means we have to allow the
        copying of str instances.
        """
        raw = {}
        for key, val in self.items():
            raw[key] = self._copy_val(val)
        return raw

    def __valtransform__(self, value):
        """
        [x] TODO:
        --------
        We might want to support specifying a list of integer ANSI codes
        or possible types other than str and list[str].
        """
        from termx.fmt import color

        if isinstance(value, str):
            # Have to use a special method to avoid circular imports.
            depth = self.base_data['COLOR_DEPTH']
            return color(value, depth=depth)
        elif isinstance(value, list):
            return [self.__valtransform__(v) for v in value]
        elif isinstance(value, color):
            return value
        else:
            raise ConfigValueError(value)


class IconsDoc(SectionDoc):

    class Meta:
        CONFIG_KEY = 'ICONS'
        NOT_CONFIGURABLE = ()


class TextDoc(FormatSectionDoc):

    class Meta:
        CONFIG_KEY = 'TEXT'
        # Format Obj Treats Style and Styles as the Same Thing to Not Confuse
        ALLOWED = ('COLOR', 'STYLES', 'ICON', 'STYLE', 'WRAPPER')
        NOT_CONFIGURABLE = ()


class FormatsDoc(FormatSectionDoc):

    class Meta:
        CONFIG_KEY = 'FORMATS'
        # Format Obj Treats Style and Styles as the Same Thing to Not Confuse
        ALLOWED = ('COLOR', 'STYLES', 'ICON', 'STYLE', 'WRAPPER')
        NOT_CONFIGURABLE = ()
