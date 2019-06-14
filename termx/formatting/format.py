import contextlib
from dataclasses import dataclass, field, InitVar, fields
import typing

from termx.colorlib import color as Color, style as Style

from .exceptions import FormatException


@dataclass
class FormatDataClass:

    def __post_init__(self, *args, **kwargs):
        for fld in fields(self):
            if fld.metadata and fld.metadata.get('allowed'):
                if getattr(self, fld.name) not in fld.metadata['allowed']:
                    raise ValueError('Invalid value for field %s.' % fld.name)

    @property
    def __dict__(self):
        data = {}
        for fld in fields(self):
            if fld.init:
                if fld.metadata and fld.metadata.get('dict_field'):
                    data[fld.metadata['dict_field']] = getattr(self, fld.name)
                else:
                    data[fld.name] = getattr(self, fld.name)
        return data

    def copy(self):
        data = self.__dict__.copy()
        return type(self)(**data)

    def new_with(self, **kwargs):
        data = self.__dict__.copy()
        data.update(**kwargs)
        return type(self)(**data)


@dataclass
class IconFormat:

    icon: str = None
    icon_location: str = field(init=False, default=None)
    icon_before: InitVar[bool] = field(default=None)
    icon_after: InitVar[bool] = field(default=None)
    format_with_icon: bool = field(default=True)

    def __post_init__(self, icon_before, icon_after, *args, **kwargs):
            """
            Whether or not to place the icon before the text.  Defaults to True
            if neither `icon_before` or `icon_after` are set.
            """
            if icon_before is None and icon_after is None:
                self.icon_location = 'before'
            elif icon_before is not None and icon_after is None:
                if icon_before is True:
                    self.icon_location = 'before'
                else:
                    self.icon_location = 'after'
            elif icon_after is not None and icon_before is None:
                if icon_after is True:
                    self.icon_location = 'after'
                else:
                    self.icon_location = 'before'
            else:
                # Both `icon_after` and `icon_before` non null.
                if icon_after is True and icon_before is True:
                    self.icon_location = 'before'
                elif icon_after is True:
                    self.icon_location = 'after'
                else:
                    self.icon_location = 'before'

    def _apply_icon(self, text):
        if self.icon:
            if self.icon_location == 'before':
                return "%s %s" % (self.icon, text)
            return "%s %s" % (text, self.icon)
        return text

    def add_icon(self, icon):
        self.icon = icon

    def remove_icon(self):
        self.icon = None

    def with_icon(self, icon, **kwargs):
        """
        Creates and returns a copy of the Format instance with the icon.

        [x] TODO:
        --------
        Deprecate and just use `new_with` directly.
        """
        return self.new_with(icon=icon, **kwargs)

    def without_icon(self):
        """
        Creates and returns a copy of the Format instance without an icon.
        """
        return self.new_with(icon=None)


@dataclass
class WrapperFormat:

    wrapper: str = None
    format_with_wrapper: bool = False

    def _apply_wrapper(self, text):
        """
        [x] TODO:
        ---------
        Investigate and implement other string formatting methods for specifying
        a wrapper that can be used to format the format object.
        """
        return self.wrapper % text

    def add_wrapper(self, wrapper, format_with_wrapper=None):
        self.wrapper = wrapper
        # Preserve Format with Wrapper if Not Specified
        self.format_with_wrapper = (format_with_wrapper
            if format_with_wrapper is not None else self.format_with_wrapper)

    def remove_wrapper(self):
        self.wrapper = None
        self.format_with_wrapper = False

    def with_wrapper(self, wrapper, format_with_wrapper=None):
        # Preserve Format with Wrapper if Not Specified
        format_with_wrapper = (format_with_wrapper
            if format_with_wrapper is not None else self.format_with_wrapper)
        return self.new_with(wrapper=wrapper, format_with_wrapper=format_with_wrapper)

    def without_wrapper(self):
        return self.new_with(wrapper=None)


@dataclass
class _Format(FormatDataClass, IconFormat, WrapperFormat):

    color: InitVar[typing.Union[Color, str]] = field(default=None, repr=False)
    _color: typing.Union[Color, str] = field(
        init=False,
        default=None,
        metadata={'dict_field': 'color'}
    )

    # Not Currently Using Background Colors
    background: InitVar[typing.Union[Color, str]] = None
    _background: typing.Union[Color, str] = field(
        init=False,
        default=None,
        metadata={'dict_field': 'background'}
    )

    styles: InitVar[typing.List[typing.Union[Style, str, int]]] = None
    _style: typing.List[typing.Union[Style, str, int]] = field(
        init=False,
        default=None,  # Cannot Default Mutable Field with []
        metadata={'dict_field': 'styles'}
    )

    def __post_init__(self, icon_before, icon_after, color, background, styles):
        """
        [x] TODO:
        ---------
        Implement background color functionality.
        """
        IconFormat.__post_init__(self, icon_before, icon_after)
        FormatDataClass.__post_init__(self)

        styles = styles or []

        self._color = color
        if self._color and not isinstance(self._color, Color):
            self._color = Color(self._color)

        self._background = background
        if not isinstance(background, Color):
            self._background = Color(background)  # Not Currently Used

        self._style = Style(*styles)

    def __call__(self, text, **overrides):
        """
        Performs the formatting on the provided text.

        Overrides can be specified to temporarily set the attributes on the
        format object just for the call.

        [x] TODO:
        --------
        For styles, we need to join/update the list of styles by adding the
        missing styles to the array.
        """
        text = "%s" % text

        with self._temporary_override(**overrides):
            # Apply icon and wrapper before and/or after formatting depending
            # on values of `format_with_wrapper` and `format_with_icon`.
            wrapper_bounds = self.format_bounds(self.wrapper, self.format_with_wrapper, self._apply_wrapper)
            icon_bounds = self.format_bounds(self.icon, self.format_with_icon, self._apply_icon)
            text = icon_bounds(wrapper_bounds(self._format))(text)

        return text

    def _format(self, text):
        text = self._color(text)
        return self._style(text)

    def apply_color(self, text):
        return self._color(text)

    def apply_style(self, text):
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
                if Style.supported(key):
                    if val is True:
                        # post_remove_styles.append(key)
                        self._style.add_style(key, strict=False)
                    elif val is False:
                        # post_add_styles.append(key)
                        self._style.remove_style(key, strict=False)
                # Have to Set Union of Styles
                elif key == 'styles':
                    for style in val:
                        self._style.add_style(style, strict=False)
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


def Format(color, **kwargs):
    """
    [x] TODO:
    --------
    Eventually we need to allow Format objects to be constructed without a
    required color, but currently the way we initialize the object across
    multiple repositories is Format(color, **kwargs), so we do this for
    temporary purposes of integration with the new dataclass.
    """
    return _Format(color=color, **kwargs)
