from termx.utils import ensure_iterable


ESCAPE_CHAR = "\x1b"


def ANSI_CHAR(*codes):
    if len(codes) != 1:
        seq = ';'.join(["%s" % code for code in codes])
    else:
        seq = codes[0]
    return "%s[%sm" % (ESCAPE_CHAR, seq)


RESET = ANSI_CHAR(0)


class formatter(object):

    def __init__(self, *args):
        self._ansi_codes = ensure_iterable(*args, coercion=tuple, force_coerce=True)

    def __call__(self, text):
        return self._formatter % ("%s" % text)

    @classmethod
    def get_ansi_sequence(cls, *args, **kwargs):
        initialized_cls = cls(*args, **kwargs)
        return initialized_cls._ansi_sequence

    @classmethod
    def get_ansi_codes(cls, *args, **kwargs):
        initialized_cls = cls(*args, **kwargs)
        return initialized_cls.ansi_codes

    @property
    def _ansi_sequence(self):
        """
        Returns the ANSI code sequence for a given color string.

        [x] IMPORTANT
        -------------
        This is the only purpose of keeping plumbum around: they support flexible
        color string identification, such as 'red' and HEX colors like '#EFEFEF'.

        For this case, we could just do colors.fg(...).ansi_sequence, but we want to
        start removing reliance on plumbum's library.
        """
        return ANSI_CHAR(*self.ansi_codes)

    @property
    def _formatter(self):
        return self._ansi_sequence + "%s" + RESET
