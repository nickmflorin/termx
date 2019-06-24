from .library import remove_pybyte_data
from .ext import get_app_root, get_root
from .playground import playground


def run_playground():
    """
    This module is only for developer environments.

    Creating a sub-module where we can store test code, duplicate and modified versions
    of existing code and explore programming possibilities is a crucial part of
    this project.

    It is in this module where we play around with certain packages, code and
    ideas, not being in the Cement app framework but still having access to the
    components that make up the instattack app.

    [x] TODO:
    --------
    Remove from production distribution/package.
    """
    playground()


def clean():
    root = get_app_root()
    print('Cleaning %s' % root)
    remove_pybyte_data(root)


def cleanroot():
    root = get_root()
    print('Cleaning %s' % root)
    remove_pybyte_data(root)
