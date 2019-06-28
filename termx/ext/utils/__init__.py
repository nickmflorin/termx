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
This file should contain utilities that are meant  for use both inside of the
package and by potential users of the package.

Utilities that are private to the package should be placed in framework.py.
"""

import asyncio
from functools import wraps
import re
import sys

from .formatting import *  # noqa


def escape_ansi_string(value):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', value)


def measure_ansi_string(value):
    bare = escape_ansi_string(value)
    return len(bare)


def percentage(num1, num2):
    return f"{'{0:.2f}'.format((num1 / num2 * 100))} %"


def progress(num1, num2):
    return f"{num1}/{num2} ({'{0:.2f} %)'.format((num1 / num2 * 100))}"


def break_before(fn):
    """
    [x] TODO:
    --------
    Add compatibility checks for Python3 and asyncio module.
    """
    if asyncio.iscoroutinefunction(fn):

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            sys.stdout.write("\n")
            return await fn(*args, **kwargs)
        return wrapper

    else:

        @wraps(fn)
        def wrapper(*args, **kwargs):
            sys.stdout.write("\n")
            return fn(*args, **kwargs)
        return wrapper


def break_after(fn):
    """
    [x] TODO:
    --------
    Add compatibility checks for Python3 and asyncio module.
    """
    if asyncio.iscoroutinefunction(fn):

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            results = await fn(*args, **kwargs)
            sys.stdout.write("\n")
            return results
        return wrapper

    else:

        @wraps(fn)
        def wrapper(*args, **kwargs):
            results = fn(*args, **kwargs)
            sys.stdout.write("\n")
            return results
        return wrapper
