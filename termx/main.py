from .library import remove_pybyte_data
from .ext import get_app_root, get_root


def clean():
    root = get_app_root()
    print('Cleaning %s' % root)
    remove_pybyte_data(root)


def cleanroot():
    root = get_root()
    print('Cleaning %s' % root)
    remove_pybyte_data(root)
