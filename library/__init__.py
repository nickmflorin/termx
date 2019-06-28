"""
This module is going to simply hold utilities that I have written that I want
to use across multiple projects.  It is only here until I find a better place
to hold them, but they are useful for multiple projects.
"""
import datetime
import os
import collections
import pathlib
import subprocess


def find_first_parent(path, name):
    """
    Given a path and the name of a parent directory, incrementally moves upwards
    in the filesystem, directory by directory, until either the root is reached
    (when the parent is not changing) or the directory reached has the desired
    parent name.
    """
    parent = pathlib.PurePath(path)

    while True:
        new_parent = parent.parent
        if new_parent.name == name:
            return new_parent
        # At the root: PurePosixPath('/'), path.parent = path.parent.parent.
        elif new_parent == parent:
            return new_parent
        else:
            parent = new_parent


def path_up_until(path, piece):

    path = pathlib.PurePath(path)
    if piece not in path.parts:
        raise ValueError(f'The path does not contain {piece}.')

    index = path.parts.index(piece)
    parts = path.parts[:index + 1]
    return os.path.join(*parts)


def relative_to_app_root(path, app_name):
    """
    This assumes that the app root is one level lower than the root that we
    are referring to:
    > Root
    >>  App Root
    >>>>  Module 1
    >>>>  Module 2
    """
    path = pathlib.PurePath(path)
    if app_name not in path.parts:
        raise ValueError('%s not in root path.' % app_name)

    ind = path.parts.index(app_name)
    try:
        parts = path.parts[ind + 1:]
    except IndexError:
        parts = path.parts[ind:]
    return os.path.join(*parts)


def relative_to_root(path, app_name):
    """
    This assumes that the app root is one level lower than the root that we
    are referring to:
    > Root
    >>  App Root
    >>>>  Module 1
    >>>>  Module 2
    """
    path = pathlib.PurePath(path)
    if app_name not in path.parts:
        raise ValueError('%s not in root path.' % app_name)

    ind = path.parts.index(app_name)
    parts = path.parts[ind:]
    return os.path.join(*parts)


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
        # if type(value) not in [str, bytes, int, float, bool]:
        #     raise ValueError('Cannot guarantee coercion of type %s.' % value)
        return coercion([value])


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


def remove_pybyte_data(*paths):

    def _remove_pybyte_data(pt):
        [p.unlink() for p in pathlib.Path(pt).rglob('*.py[co]')]
        [p.rmdir() for p in pathlib.Path(pt).rglob('__pycache__')]

    [_remove_pybyte_data(pt) for pt in paths]
