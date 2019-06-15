from termx.ext.compat import safe_text
from termx.core.exceptions import ColorLibError


def ansi_sequence_from_codes(*codes):
    """
    [x] NOTE:
    -------
    There is a circular import issue with the relationship between colour.py,
    config and this utility.

    If we try to import config.constants here to access constants.ANSI_ESCAPE_CHAR,
    we get an issue because config.configure imports colour.py, and colour.py
    imports this file, which would then be importing config.
    """
    ANSI_ESCAPE_CHAR = "\x1b"

    for cd in codes:
        if not isinstance(cd, int):
            raise ColorLibError('ANSI codes must be integers.')

    if len(codes) != 1:
        seq = ';'.join(["%s" % code for code in codes])
    else:
        seq = codes[0]
    # return "%s[%sm" % (constants.ANSI_ESCAPE_CHAR, seq)
    return "%s[%sm" % (ANSI_ESCAPE_CHAR, seq)


class abstract_formatter(object):
    """
    Abstract base class for ANSII based formatting objects.
    """
    RESET = ansi_sequence_from_codes(0)

    def __call__(self, text):
        """
        [x] TODO:
        --------
        Investigate other means of formatting the text for user convenience, so
        that different types of format strings can be manually created.
        """
        return self.formatter(text)

    @classmethod
    def reset(cls, text):
        return "%s%s" % (text, cls.RESET)

    @classmethod
    def get_ansi_sequence(cls, *args, **kwargs):
        initialized_cls = cls(*args, **kwargs)
        return initialized_cls._ansi_sequence

    @classmethod
    def get_ansi_codes(cls, *args, **kwargs):
        initialized_cls = cls(*args, **kwargs)
        return initialized_cls.ansi_codes

    @property
    def ansi_sequence(self):
        """
        Returns the ANSI code sequence for a given color string.

        [x] IMPORTANT
        -------------
        This is the only purpose of keeping plumbum around: they support flexible
        color string identification, such as 'red' and HEX colors like '#EFEFEF'.

        For this case, we could just do colors.fg(...).ansi_sequence, but we want to
        start removing reliance on plumbum's library.
        """
        if len(self.ansi_codes) == 0:
            raise ColorLibError('Cannot generate ANSI sequence for empty set of ANSI codes.')
        return ansi_sequence_from_codes(*self.ansi_codes)

    @property
    def formatter(self):
        """
        [x] Note:
        --------
        Since we are now generating these sequences on our own and separating styles
        from colors, we will not have the combined ANSII sequences that we would
        see with Plumbum (since Plumbum treated colors.bold and colors.blue as
        the same operation).

        [!] We should see if there is a way for us to do that, since it makes the
        ANSII output a lot cleaner.
        """
        def _formatter(text):
            try:
                seq = self.ansi_sequence
            except ColorLibError:
                return text
            else:
                # [x] TODO:
                # We might want to apply safe_text() to the overall output here.
                return self.reset("%s%s" % (seq, safe_text(text)))

        return _formatter
