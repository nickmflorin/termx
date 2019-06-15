import plumbum
from plumbum import colors

from termx.ext.utils import ensure_iterable
from termx.core.exceptions import InvalidColor, InvalidStyle

from .base import abstract_formatter
from .style import style


class color(abstract_formatter):
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

        [x] NOTE:
        --------
        For whatever reason, plumbum colors library returns a sequence of codes
        for a single color, most likely because it is making assumptions about
        other styles/settings on the color.

        We want to just return the first code in the list.
        """
        try:
            color = colors.fg(self._value)
        except plumbum.colorlib.styles.ColorNotFound:
            raise InvalidColor(self._value)
        else:
            # e.g. [38, 2, 239, 239, 239]
            return ensure_iterable(color.ansi_codes[0], coercion=list, force_coerce=True)
