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


def get_root(NAME=None):
    """
    Given the path of the file calling the function, incrementally moves up
    directory by directory until either the root is reached (when the parent
    is not changing) or the directory reached has the name associated with
    the app name.

    When we reach the directory associated with the app directory, the root
    is the path's parent.
    """
    path = os.path.dirname(os.path.realpath(__file__))

    if not NAME:
        from termx.config import settings
        NAME = settings.NAME

    parent = find_first_parent(path, NAME)
    return str(parent.parent)


def get_app_root(NAME=None):

    if not NAME:
        from termx.config import settings
        NAME = settings.NAME

    root = get_root(NAME=NAME)
    return os.path.join(root, NAME)


def get_root_file_path(filename, NAME=None, ext=None):
    if ext:
        filename = "%s.%s" % (filename, ext)
    root = get_root(NAME=NAME)
    return os.path.join(root, filename)
