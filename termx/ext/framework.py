"""
[x] NOTE:
--------
Because the ext module is used both at the upper levels by setuptools, the config
and at lower levels in core, it is important that all imports into the files
in these modules be lazy imported.

The functionality in these modules should not depend on functionality elsehwhere
in the app, except for top level constants.

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

    # Temporary, Import Not Working
    # from termx import __NAME__
    __NAME__ = 'termx'

    path = os.path.dirname(os.path.realpath(__file__))
    parent = find_first_parent(path, __NAME__)
    return str(parent.parent)


def get_app_root():
    # Temporary, Import Not Working
    # from termx import __NAME__
    __NAME__ = 'termx'

    root = get_root()
    return os.path.join(root, __NAME__)


def get_root_file_path(filename, ext=None):
    if ext:
        filename = "%s.%s" % (filename, ext)
    root = get_root()
    return os.path.join(root, filename)
