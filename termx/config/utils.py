import os
import collections
import yaml

from termx.ext.framework import get_app_root

from .constants import CONFIG_ROOT_DIR, CONFIG_FILE_NAME


def read_default_config():
    from .doc import ConfigDoc

    root = get_app_root()
    CONFIG_FILE_PATH = os.path.join(root, CONFIG_ROOT_DIR, CONFIG_FILE_NAME)

    with open(CONFIG_FILE_PATH, 'r') as f:
        doc = yaml.load(f)
    return ConfigDoc(doc)


class ConfigMapping(collections.MutableMapping):
    """
    Dict subclass specifically for configuration that adds flexibility to how
    items are retrieved and stores keys and values by uppercase transformations.
    """

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key.upper()

    def __repr__(self):
        return "%s" % self.store

    def __dict__(self):
        return self.store
