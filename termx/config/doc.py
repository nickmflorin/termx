import copy
import logging
import warnings

from simple_settings import settings

from termx.exceptions import ConfigError, InconfigurableError, ConfigValueError


logger = logging.getLogger('Configuration')


class ConfigDoc(dict):
    """
    Dict subclass specifically for configuration that adds flexibility to how
    items are retrieved and stores keys and values by uppercase transformations.
    """

    # The only object instances we can store in settings other than instances
    # of ConfigDoc.
    MAINTAINABLE_OBJECTS = ('color', 'style', 'highlight', 'Format')

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        return super(ConfigDoc, self).__getitem__(self.__keytransform__(key))

    def __setitem__(self, key, value):
        try:
            value = self.__valtransform__(value)
        except ConfigError as e:
            self._handle_config_error(e)
        else:
            super(ConfigDoc, self).__setitem__(
                self.__keytransform__(key),
                value
            )

    def __delitem__(self, key):
        super(ConfigDoc, self).__delitem__(self.__keytransform__(key))

    def __keytransform__(self, key):
        if not key.startswith('__'):
            return key.upper()
        return key

    def __valtransform__(self, value):
        """
        [x] TODO:
        --------
        Figure out how to track initialization and then raise an exception if
        we are setting a value as a raw dictionary vs. ConfigDoc instance after
        initialization has occured.
        """
        if isinstance(value, ConfigDoc) or (
                hasattr(value, '__class__')
                and value.__class__.__name__ in self.MAINTAINABLE_OBJECTS):
            return value

        # This Only Happens on Initialization
        if isinstance(value, dict):
            return ConfigDoc(value)

        elif isinstance(value, str):
            return value.upper()

        elif isinstance(value, int):
            return value

        elif isinstance(value, list):
            return [
                self.__valtransform__(v)
                for v in value
            ]

        else:
            raise ConfigValueError(value)

    def __deepcopy__(self, memo):
        """
        Required for simple_settings module.

        Since simple_settings expects dict instances to be valid parameters
        to copy.deepcopy(), we need to establish how to deepcopy ConfigDoc
        instances.

        In order to maintain custom ConfigDoc dicts with termx objects as
        values (i.e. color, style, Format, etc.) we need to establish a
        __deepcopy__ method for each sub-doc (Colors, Formats, etc.) that
        copies these objects manually.

        Non ConfigDoc instances can be copied as normal.
        """
        raw = {}
        for key, val in self.items():
            if isinstance(val, ConfigDoc):
                raw[key] = val.__deepcopy__(memo)
            else:
                raw[key] = copy.deepcopy(val)
        return raw

    def update(self, *args, **kwargs):
        """
        For ConfigDoc instances, we only want to override the nested field in
        a nested object, if the nested object is being updated, instead of
        replacing the entire object.

        [x] TODO:
        --------
        This is where we might want to check if a certain doc is allowed to
        add new fields.

        >>> data = {'colors': {'gray': '#EFEFEF', 'black': '#000000'}}
        >>> doc = ConfigDoc(data)
        >>> doc.update({'colors': {'black': '#111111'})
        >>> doc.__dict__
        >>> {'colors': {'gray': '#EFEFEF', 'black': '#111111'}}
        """
        def update_value(k, v):
            """
            Applied after we check if the value exists in the doc and if it
            is allowed to be reconfigured.
            """
            if k in self:
                if isinstance(self[k], ConfigDoc):
                    if isinstance(v, dict):
                        self[k].update(**v)
                    elif isinstance(v, ConfigDoc):  # Allow Merging of ConfigDoc Instances
                        self[k].update(v.__dict__)
                    else:
                        # Prevent overrides like:
                        # >>> doc.update({'colors': 'blue'})
                        raise ConfigValueError(v)
                else:
                    self.__setitem__(k, v)
            else:
                self.__setitem__(k, v)

        # Right now, we have to suppress this error because of the backwards
        # reference methods.  For instance, self['COLORS']['SHADES'] will be
        # set with initial values ['BLACK', 'LIGHT_BLACK', ...] and then
        # updated again to set the actual HEX values.
        for k, v in dict(*args, **kwargs).items():
            update_value(k, v)
            # if k in self:
            #     try:
            #         self._raise_if_nonconfigurable_field(k)
            #     except ConfigError as e:
            #         self._handle_config_error(e)
            #     else:
            #         update_value(k, v)
            # else:
            #     update_value(k, v)

    @property
    def non_configurable_fields(self):
        fields = self._meta('NOT_CONFIGURABLE')
        return [fld.upper() for fld in fields]

    @classmethod
    def _handle_config_error(cls, e):
        if settings.STRICT_CONFIG:
            raise e
        warnings.warn(str(e))
        logger.warn(str(e))

    def _raise_if_nonconfigurable_field(self, attr):
        """
        Raises an exception if a certain field is in the default config file
        and is not overridable, but an attempt to override the value is made
        after settings are initialized.
        """
        if attr in self.non_configurable_fields:
            raise InconfigurableError(attr)
