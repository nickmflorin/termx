# -*- coding: utf-8 -*-
import sys


PY2 = sys.version_info[0] == 2
ENCODING = "utf-8"


if PY2:
    builtin_str = str
    bytes = str
    str = unicode  # noqa
    basestring = basestring  # noqa

    def iteritems(dct):
        return dct.iteritems()


else:
    builtin_str = str
    bytes = bytes
    str = str
    basestring = (str, bytes)

    def iteritems(dct):
        return dct.items()


def to_unicode(text_type, encoding=ENCODING):
    if isinstance(text_type, bytes):
        return text_type.decode(encoding)
    return text_type


def safe_text(text):
    if PY2:
        return to_unicode(text)
    return text
