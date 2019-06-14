import contextlib

from termx.colorlib import color as _color, _style

from .exceptions import FormatException
from .mixins import IconMixin, WrapperMixin


class Format(IconMixin, WrapperMixin):

    def __init__(
        self,
        color=None,
        styles=None,
        # background = None,
        wrapper=None,
        format_with_wrapper=False,
        icon=None,
        icon_before=None,
        icon_after=None,
        format_with_icon=True,
    ):
        """
        [x] TODO:
        --------
        We eventually want to deprecate (I think) the keyword argument specifications
        for `bold` and `underline` and instead initialize as:
        >>> styles=['bold', 'underline']

        The color will eventually be initialized with the background color as
        well.
        """
        self._color = _color(color)
        self._style = _style(*(styles or []))

        IconMixin.__init__(self, icon=icon, icon_before=icon_before, icon_after=icon_after, format_with_icon=format_with_icon)
        WrapperMixin.__init__(self, wrapper=wrapper, format_with_wrapper=format_with_wrapper)

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
            text = icon_bounds(wrapper_bounds(self._format))(text)

        return text

    def _format(self, text):
        text = self.color(text)
        return self.style(text)

    def color(self, text):
        return self._color(text)

    def style(self, text):
        return self._style(text)

    def add_style(self, style_name):
        if not self._style.has_style(style_name):
            self._style.add_style(style_name)

    def remove_style(self, style_name):
        if self._style.has_style(style_name):
            self._style.remove_style(style_name)

    def remove_text_decoration(self):
        """
        [x] TODO:
        --------
        Should we be more selective in how we use this, and only remove styles
        that are more specific to things like underline, bold, strikethrough,
        etc.?
        """
        self._style.clear_decoration()

    def with_style(self, style_name):
        fmt = self.copy()
        fmt.add_style(style_name)
        return fmt

    def without_text_decoration(self):
        fmt = self.copy()
        fmt.remove_text_decoration()
        return fmt

    def copy(self, **overrides):
        """
        [x] TODO:
        --------
        Possibly Deprecate

        [x] IMPORTANT
        -------------
        This might cause issues depending on the mutability of the style
        and color objects!
        """
        data = self.__dict__.copy()
        data.update(**overrides)
        return Format(**data)

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

    @contextlib.contextmanager
    def _temporary_override(self, **overrides):
        """
        Temporarily overrides the instance with values provided on __call__
        so that the values can be used to format the text without mutating
        the original Format instance.

        [x] IMPORTANT
        -------------
        This might cause issues depending on the mutability of the style
        and color objects!
        """
        original = self.__dict__.copy()

        # I don't think we need this since we set the original style object
        # afterwards.
        # post_add_styles = []
        # post_remove_styles = []

        try:
            # We allow the style attributes to be changed to be passed in as
            # keyword arguments with boolean values.
            for key, val in overrides.items():
                if _style.supported(key):
                    if val is True:
                        # post_remove_styles.append(key)
                        self._style.add_style(key, strict=False)
                    elif val is False:
                        # post_add_styles.append(key)
                        self._style.remove_style(key, strict=False)
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
