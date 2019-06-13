import contextlib
from plumbum import colors

from .exceptions import FormatException


__all__ = (
    'Format',
)


class IconMixin(object):

    def __init__(self, icon=None, icon_before=None, icon_after=None, format_with_icon=True):
        self.icon = self.icon_before = self.icon_after = None
        self.format_with_icon = format_with_icon
        if icon:
            self.add_icon(
                icon=icon,
                icon_before=icon_before,
                icon_after=icon_after,
                format_with_icon=format_with_icon,
            )

    def _iconize(self, text):
        if self.icon:
            if self._icon_before:
                return "%s %s" % (self.icon, text)
            return "%s %s" % (text, self.icon)
        return text

    def remove_icon(self):
        self.icon = self.icon_after = self.icon_before = None

    def add_icon(self, icon, icon_before=None, icon_after=None, format_with_icon=True):
        self.icon = icon
        self.icon_after = icon_after
        self.icon_before = icon_before
        self.format_with_icon = format_with_icon

    def with_icon(self, icon, icon_before=None, icon_after=None, format_with_icon=True):
        """
        Creates and returns a copy of the Format instance with the icon.
        """
        fmt = self.copy()
        fmt.add_icon(icon, icon_before=icon_before, icon_after=icon_after,
            format_with_icon=format_with_icon)
        return fmt

    def without_icon(self):
        """
        Creates and returns a copy of the Format instance without an icon.
        """
        fmt = self.copy()
        fmt.remove_icon()
        return fmt

    @property
    def __icon_dict__(self):
        return {
            'icon': self.icon,
            'icon_before': self.icon_before,
            'icon_after': self.icon_after,
            'format_with_icon': self.format_with_icon
        }

    @property
    def _icon_before(self):
        """
        Whether or not to place the icon before the text.  Defaults to True
        if neither `icon_before` or `icon_after` are set.
        """
        if self.icon_before is None and self.icon_after is None:
            return True
        elif self.icon_before is None:
            return not self.icon_after
        else:
            return self.icon_before

    @property
    def _icon_after(self):
        """
        Whether or not to place the icon after the text.  Defaults to False
        if neither `icon_before` or `icon_after` are set.
        """
        if self.icon_before is None and self.icon_after is None:
            return False
        elif self.icon_after is None:
            return not self.icon_before
        else:
            return self.icon_before


class WrapperMixin(object):

    def __init__(self, wrapper=None, format_with_wrapper=None):
        self.wrapper = wrapper
        self.format_with_wrapper = format_with_wrapper

    @property
    def __wrapper_dict__(self):
        return {
            'wrapper': self.wrapper,
            'format_with_wrapper': self.format_with_wrapper,
        }

    def _wrap(self, text):
        return self.wrapper % text

    def add_wrapper(self, wrapper, format_with_wrapper=False):
        self.wrapper = wrapper
        self.format_with_wrapper = format_with_wrapper

    def remove_wrapper(self):
        self._wrapper = None
        self._format_with_wrapper = False

    def with_wrapper(self, wrapper, format_with_wrapper=None):
        fmt = self.copy()
        fmt._wrapper = wrapper

        # Preserve Format with Wrapper if Not Specified
        fmt._format_with_wrapper = format_with_wrapper
        if fmt._format_with_wrapper is None:
            fmt._format_with_wrapper = self.format_with_wrapper
        return fmt

    def without_wrapping(self):
        fmt = self.copy()
        fmt.remove_wrapper()
        return fmt


class DecorativeMixin(object):

    DECORATIONS = [colors.underline, colors.bold]

    def __init__(self, bold=False, underline=False):
        if bold:
            self.add_bold()
        if underline:
            self.add_underline()

    @property
    def is_bold(self):
        return colors.bold in self._colors

    @property
    def is_underline(self):
        return colors.underline in self._colors

    def add_bold(self):
        if not self.is_bold:
            self._colors.append(colors.bold)

    def add_underline(self):
        if not self.is_underline:
            self._colors.append(colors.underline)

    def remove_bold(self):
        if self.is_bold:
            self._colors.remove(colors.bold)

    def remove_underline(self):
        if self.is_underline:
            self._colors.remove(colors.underline)

    def remove_text_decoration(self):
        if self.is_bold or self.is_underline:
            self.remove_underline()
            self.remove_bold()

    def with_underline(self):
        fmt = self.copy()
        fmt.add_underline()
        return fmt

    def with_bold(self):
        fmt = self.copy()
        fmt.add_bold()
        return fmt

    def without_text_decoration(self):
        fmt = self.copy()
        fmt.remove_text_decoration()
        return fmt


class Format(IconMixin, WrapperMixin, DecorativeMixin):

    def __init__(
        self,
        *args,
        wrapper=None,
        format_with_wrapper=False,
        icon=None,
        icon_before=None,
        icon_after=None,
        format_with_icon=True,
        bold=False,
        underline=False,
    ):
        self._colors = list(args)

        IconMixin.__init__(self, icon=icon, icon_before=icon_before, icon_after=icon_after, format_with_icon=format_with_icon)
        WrapperMixin.__init__(self, wrapper=wrapper, format_with_wrapper=format_with_wrapper)
        DecorativeMixin.__init__(self, bold=bold, underline=underline)

    def format_bounds(self, element, format_with, formatter):
        """
        Returns a decorator that is used to wrap the base formatting function
        with a formatting function that is either applied before or after the
        base function is applied.

        This makes an annoying/ugly programming application more straight forward
        to apply repeatedly.  Although it is only used for icons and text wrapping
        now, we will likely need it for future cases.

        If `element_attr` is specified for the format object, it is applied with
        `formatter` before the base formatting function if the value of `format_with`
        is True, and applied after the base formatting function if `format_with`
        is False.
        """
        def decorator(func):

            def wrapped(text):
                if element and format_with:
                    text = formatter(text)

                text = func(text)

                if element and not format_with:
                    text = formatter(text)

                return text

            return wrapped
        return decorator

    def __call__(self, text, **overrides):
        """
        Performs the formatting on the provided text.
        Overrides can be specified to temporarily set the attributes on the
        format object just for the call.
        Colors should not be specified in the overrides...
        """
        text = "%s" % text

        with self._temporary_override(**overrides):

            # Apply icon and wrapper before and/or after formatting depending
            # on values of `format_with_wrapper` and `format_with_icon`.
            wrapper_bounds = self.format_bounds(self.wrapper, self.format_with_wrapper, self._wrap)
            icon_bounds = self.format_bounds(self.icon, self.format_with_icon, self._iconize)
            text = icon_bounds(wrapper_bounds(self._colorize))(text)

        return text

    def _colorize(self, text):
        c = colors.do_nothing
        for i in range(len(self._colors)):
            c = c & self._colors[i]
        return (c | text)

    @contextlib.contextmanager
    def _temporary_override(self, **overrides):
        """
        Temporarily overrides the instance with values provided on __call__
        so that the values can be used to format the text without mutating
        the original Format instance.
        """
        original = self.__dict__.copy()
        del original['colors']

        remove_bold = remove_underline = False
        add_bold = add_underline = False

        try:
            for key, val in overrides.items():
                if key == 'bold':
                    if val is True and not self.is_bold:
                        remove_bold = True
                        self.add_bold()
                    elif val is False and self.is_bold:
                        add_bold = True
                        self.remove_bold()

                elif key == 'underline':
                    if val is True and not self.is_underline:
                        remove_underline = True
                        self.add_underline()
                    elif val is False and self.is_underline:
                        add_underline = True
                        self.remove_underline()
                else:
                    try:
                        setattr(self, key, val)
                    except AttributeError:
                        raise FormatException(f'Invalid format attribute {key}.')
            yield self

        finally:
            for key, val in original.items():
                try:
                    setattr(self, key, val)
                except AttributeError:
                    raise FormatException(f'Invalid format attribute {key}.')

            if add_bold:
                self.add_bold()
            elif remove_bold:
                self.remove_bold()

            if add_underline:
                self.add_underline()
            elif remove_underline:
                self.remove_underline()
            return None

    @property
    def colors(self):
        return [
            c for c in self._colors
            if c not in self.DECORATIONS
        ]

    @property
    def __dict__(self):
        base_dict = {'colors': self._colors}
        base_dict.update(**self.__wrapper_dict__)
        base_dict.update(**self.__icon_dict__)
        return base_dict

    def copy(self, **overrides):
        data = self.__dict__.copy()
        data.update(**overrides)
        colors = data.pop('colors')
        return Format(*colors, **data)

    def format_with(self, *args, **kwargs):
        """
        Returns a copy of the original Format instance with additional colors
        and options specified.
        """
        new_colors = []
        for arg in args:
            if arg not in self._colors:
                new_colors.append(arg)
        colors = list(self._colors) + new_colors
        kwargs['colors'] = colors
        return self.copy(**kwargs)
