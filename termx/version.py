from .utils import get_version as _get_version


__NAME__ = 'termx'
VERSION = (0, 0, 2, 'alpha', 0)


def get_version(version=VERSION):
    return _get_version(version)
