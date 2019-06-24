"""
[x] THIS FILE
------------
This file should contain utilities that are meant solely for private use
with in the package.

Utilities meant for use both inside the package and by potential users should
be placed in the utils.py file.
"""

import os
from termx.library import find_first_parent


def get_root():
    """
    Given the path of the file calling the function, incrementally moves up
    directory by directory until either the root is reached (when the parent
    is not changing) or the directory reached has the name associated with
    the app name.

    When we reach the directory associated with the app directory, the root
    is the path's parent.
    """
    from termx import settings
    path = os.path.dirname(os.path.realpath(__file__))
    parent = find_first_parent(path, settings.NAME)
    return str(parent.parent)


def get_app_root():
    from termx import settings
    root = get_root()
    return os.path.join(root, settings.NAME)


def get_root_file_path(filename, ext=None):
    if ext:
        filename = "%s.%s" % (filename, ext)
    root = get_root()
    return os.path.join(root, filename)
