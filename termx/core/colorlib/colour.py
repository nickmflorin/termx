import plumbum
from plumbum import colors

from termx.ext.utils import ensure_iterable
from termx.core.exceptions import InvalidColor, InvalidStyle

from .base import abstract_formatter
from .style import style


"""
Packages to Consider
--------------------
pip install ansicolors

>>> green('green on black', bg='black', style='underline')
>>> red('very important', style='bold+underline')
>>> color('nice color', 'white', '#8a2be2')

Plumbum
-------
Plumbum colors.fg(), colors.bg() or colors.attr returns an object
<ANSIStyle: Background Green>.

The following properties/methods might be useful:
(1) from_ansi
(2) from_color
(3) full
(4) wrap
(5) attributes
(6) fg
(7) bg
(8) from_ansi
(9) from_color
(10) add_ansi
(11) ansi_codes >>> [38, 2, 239, 239, 239]
(12) ansi_sequence >>> '\x1b[38;2;239;239;239m'
(13) attribute_names
(14) attributes
(15) string_contains_colors

Resolution/Terminal Related Properties:

(1) .basic (8 color) ==> ANSI Codes [x]
(2) .simple (16 color) ==> ANSI Codes [x, x] ??
        SpringGreen3 -> Green (Useful for Curses!!!)
(3) .full (256 color) ==> ANSI Codes [x, x, x]
(4) .true (24 bit color) ==> ANSI Codes [x, x, x, x, x]

[x] IMPORTANT
-------------
The reason we are seeing divergences in the colors when we use HEX information
is because of the display type.

Certain HEX colors

    >>> colors.fg('#28a745')

will default to a certain type, which is usually `full`.

[x] TODO:
--------
We need to determine what type of color support the given terminal has
and restrict the output of the plumbum colors.  For our cases, it seems
we always have problems with the 24 bit colors.

[x] NOTE:
--------
We cannot just slice the ansi codes:

    >>> color = colors.fg('#28a745')

    >>> color.true.ansi_codes
    >>> [38, 2, 40, 167, 69]

    >>> color.full.ansi_codes
    >>> [38, 5, 35]
"""


class color(abstract_formatter):

    def __init__(self, value):
        self._value = value

    def __getattr__(self, name):
        """
        We want to be able to apply styles as one-offs on a color instance as
        well, although this differs from the style object since we cannot mutate
        colors with a style object.

        >>> c = color('red')
        >>> c.faint('Test Message')  ===>  Allowed

        >>> c = color('red')
        >>> c.faint()   ===> Not Allowed, Cannot Mutate Color w/ Style

        [x] IMPORTANT:
        --------------
        This will prevent us from chaining styles on top of colors like:
        >>> c = color('red')
        >>> c.faint().underline('Test')

        This could be kind of cool if we could pull it off, although it might
        not be worth it.
        """
        try:
            code = style.code_for(name)
        except InvalidStyle:
            raise AttributeError('Color instance does not have attribute %s.' % name)
        else:
            def lazy_style(*args):
                """
                This differs from the lazy_style in the style object, since
                we cannot add style codes to a color object, we cannot mutate
                it by calling style methods:

                To do something like:

                >>> c.bold('test').underline('nick')

                We would have to return a sub-classed string object (kind of implemented
                before) that allowed the recusion of methods to be applied.
                """
                if len(args) == 0:
                    raise TypeError(
                        "When applying a style method to a color, the color instance "
                        "cannot be mutated with the style method - the method can "
                        "only be used to apply the color and style to a specified "
                        "argument, which must be provided to the style method."
                    )
                sty = style(code)
                return sty(self.__call__(args[0]))

            return lazy_style

    @property
    def ansi_codes(self):
        """
        Returns the ANSI related codes for a given color string.

        [x] IMPORTANT
        -------------
        This is the only purpose of keeping plumbum around: they support flexible
        color string identification, such as 'red' and HEX colors like '#EFEFEF'.

        It gives us a little more flexibility for the time being, but we want to do
        some things on our own to avoid having to use their library in the future.

        [x] TODO:
        --------
        Determine what type of color resolution support the given package
        user has and return colors adjusted accordingly.  There might be
        a property on the plumbum color to do this.
        """
        if isinstance(self._value, type(self)):
            return self.ansi_codes
        try:
            color = colors.fg(self._value)
        except plumbum.colorlib.styles.ColorNotFound:
            raise InvalidColor(self._value)
        else:
            # Resolution Full, Color Codes: [x, x, x]
            codes = color.full.ansi_codes
            return ensure_iterable(codes, coercion=list, force_coerce=True)
