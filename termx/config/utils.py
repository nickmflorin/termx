import copy
import logging
import warnings

from simple_settings import settings

from termx.exceptions import (
    InconfigurableError, DisallowedFieldError, ConfigValueError)


logger = logging.getLogger('Configuration')


class ConfigMapping(dict):
    """
    Dict subclass specifically for configuration that adds flexibility to how
    items are retrieved and stores keys and values by uppercase transformations.
    """

    def __init__(self, data):
        super(ConfigMapping, self).__init__(data)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        return super(ConfigMapping, self).__getitem__(self.__keytransform__(key))

    def __setitem__(self, key, value):
        super(ConfigMapping, self).__setitem__(self.__keytransform__(key), value)

    def __delitem__(self, key):
        super(ConfigMapping, self).__delitem__(self.__keytransform__(key))

    def __keytransform__(self, key):
        if not key.startswith('__'):
            return key.upper()
        return key


class ConfigDoc(ConfigMapping):
    """
    Dict subclass specifically for configuration that adds flexibility to how
    items are retrieved and stores keys and values by uppercase transformations.
    """

    def __deepcopy__(self, memo):
        return self.__class__(copy.deepcopy(dict(self)))

    def __setitem__(self, key, value):
        super(ConfigDoc, self).__setitem__(
            self.__keytransform__(key),
            self.__valtransform__(value)
        )

    @classmethod
    def _handle_config_error(cls, e):
        if settings.STRICT_CONFIG:
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
