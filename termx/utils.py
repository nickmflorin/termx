import collections
import datetime
import os
import re
import subprocess


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


def break_after(value):
    return "%s\n" % value


def filter_array(array):
    return [item for item in array if item != "" and item is not None]


def join(*parts, endline=False):
    parts = filter_array(list(parts))
    value = "".join(["%s" % part for part in parts])
    if endline:
        return break_after(value)
    return value


def space(*parts, endline=False):
    parts = filter_array(list(parts))
    value = " ".join(["%s" % part for part in parts])
    if endline:
        return break_after(value)
    return value


def laydown(*parts, endline=False):
    parts = filter_array(list(parts))

    value = "\n".join(["%s" % part for part in parts])
    if endline:
        return break_after(value)
    return value


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


def get_version(version):
    """
    Returns a PEP 386-compliant version number from VERSION.
    """
    if len(version) != 5 or version[3] not in ('alpha', 'beta', 'rc', 'final'):
        raise ValueError('Invalid version %s.' % version)

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|c}N - for alpha, beta and rc releases

    # We want to explicitly include all three version/release numbers
    # parts = 2 if version[2] == 0 else 3
    parts = 3
    main = '.'.join(str(x) for x in version[:parts])

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        git_changeset = get_git_changeset()
        if git_changeset:
            sub = '.dev%s' % git_changeset

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return main + sub


def get_git_changeset():
    """
    Returns a numeric identifier of the latest git changeset.
    The result is the UTC timestamp of the changeset in YYYYMMDDHHMMSS format.

    This value isn't guaranteed to be unique, but collisions are very
    unlikely, so it's sufficient for generating the development version
    numbers.
    """
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_log = subprocess.Popen('git log --pretty=format:%ct --quiet -1 HEAD',
       stdout=subprocess.PIPE,
       stderr=subprocess.PIPE,
       shell=True,
       cwd=repo_dir,
       universal_newlines=True)

    timestamp = git_log.communicate()[0]
    try:
        timestamp = datetime.datetime.utcfromtimestamp(int(timestamp))
    except ValueError:  # pragma: nocover
        return None     # pragma: nocover
    return timestamp.strftime('%Y%m%d%H%M%S')
