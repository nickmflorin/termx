import plumbum

from termx.utils import ensure_iterable

from .base import formatter
from .exceptions import InvalidColor, InvalidStyle
from .style import style


class color(formatter):
    """
    [x] TODO:
    --------
    Allow multiple values to be specified, the first is reauired and the
    second optional argument would specify the background color.
    """

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
            return super(color, self).__getattr__(name)
        else:
            def lazy_style(text):
                """
                This differs from the lazy_style in the style object, since
                we cannot add style codes to a color object, we cannot mutate
                it by calling style methods:

                To do something like:

                >>> c.bold('test').underline('nick')

                We would have to return a sub-classed string object (kind of implemented
                before) that allowed the recusion of methods to be applied.
                """
                sty = style(code)
                return sty(self.__call__(text))

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
        """
        try:
            color = plumbum.colors.fg(self._value)
        except plumbum.colorlib.styles.ColorNotFound:
            raise InvalidColor(self._value)
        else:
            # e.g. [38, 2, 239, 239, 239]
            return ensure_iterable(color.ansi_codes, coercion=list, force_coerce=True)
