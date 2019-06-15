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

import re
import collections


def string_format_tuple(value):
    """
    Recursively formats a tuple and nested tuples into string format.
    """
    value = list(value)
    formatted = []

    for item in value:
        if isinstance(item, tuple):
            formatted.append(string_format_tuple(item))
        else:
            formatted.append("%s" % item)

    return '(' + ', '.join(formatted) + ')'


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


def humanize_list(value, callback=str, conjunction='and', oxford_comma=True):
    """
    Turns an interable list into a human readable string.
    >>> list = ['First', 'Second', 'Third', 'fourth']
    >>> humanize_list(list)
    u'First, Second, Third, and fourth'
    >>> humanize_list(list, conjunction='or')
    u'First, Second, Third, or fourth'
    """

    num = len(value)
    if num == 0:
        return ""
    elif num == 1:
        return callback(value[0])
    s = u", ".join(map(callback, value[:num - 1]))
    if len(value) >= 3 and oxford_comma is True:
        s += ","
    return "%s %s %s" % (s, conjunction, callback(value[num - 1]))


def ensure_iterable(value, coercion=tuple, force_coerce=False):
    """
    Some of the checking here is definitely overkill, and we should look into
    exactly what we want to use to define an iterable.  It should exclude
    generates, string objects, file objects, bytes objects, etc.  Just because
    it has an __iter__ method does not mean it should be considered an iterable
    for purposes of this method.
    """
    if (
        type(value) is not str
        and type(value) is not bytes
        and isinstance(value, collections.Iterable)
    ):
        if type(value) is list:
            if coercion is not list and force_coerce:
                return coercion(value)
            return value

        elif type(value) is tuple:
            if coercion is not tuple and force_coerce:
                return coercion(value)
            return value

        else:
            raise ValueError('Invalid iterable type %s.' % type(value))
    else:
        if type(value) not in [str, bytes, int, float, bool]:
            raise ValueError('Cannot guarantee coercion of type %s.' % value)
        return coercion([value])


def shaded_level(level, bold=False, dark_limit=0, light_limit=None, gradient=1):
    """
    [x] TODO:
    --------
    It is not a good idea right now to use the `gradient` parameter, because the
    discretized shades are not extensive enough to cover a wide range of shades
    when we use that parameter.

    We should come up with an interpolation method that shades between black
    and white depending on a gradient and a certain percentage.
    """
    from termx.config.style import Colors
    from termx.core.formatting import Format
    from termx.core.exceptions import FormatError

    light_limit = light_limit or 1
    dark_limit = dark_limit or 0
    slc = slice(dark_limit, -1 * light_limit, gradient)
    shades = Colors.SHADES[slc]

    if len(shades) == 0:
        raise FormatError('Invalid shade limits.')

    styles = []
    if bold:
        styles = ['bold']

    # fmt = Format(color=shades[level], styles=styles)
    # import ipdb; ipdb.set_trace()
    try:
        return Format(color=shades[level], styles=styles)
    except IndexError:
        return Format(color=shades[-1], styles=styles)