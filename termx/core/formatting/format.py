import contextlib
import copy
from dataclasses import dataclass, field, fields, replace, InitVar
import typing

from termx.library import ensure_iterable
from termx.core.exceptions import FormatError

from termx.ext.compat import safe_text
from termx.core.colorlib.color import color as Color, highlight as Highlight
from termx.core.colorlib.style import style as Style


def format_bounds(element, format_with, formatter):
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


@dataclass
class FormatDataClass:

    def __post_init__(self, *args, **kwargs):
        for fld in fields(self):
            if fld.metadata and fld.metadata.get('allowed'):
                if getattr(self, fld.name) not in fld.metadata['allowed']:
                    raise ValueError('Invalid value for field %s.' % fld.name)

    def _initialization_kwargs(self, **overrides):
        """
        If an empty list is passed in for the styles, or None, we assume the
        user wants to remove the styles.  Otherwise, styles are applied on
        top of the currenet styles.  We also allow styles to be explicitly
        specified as True or False.
        """
        data = copy.deepcopy(self.__dict__)
        for key, val in overrides.items():

            if Style.supported(key):
                if val is True:
                    data['styles'].add_style(key, strict=False)
                elif val is False:
                    data['styles'].remove_style(key, strict=False)
                else:
                    raise ValueError(f'{key} must be speceified as True or False')

            # Have to Set Union of Styles
            elif key == 'styles':
                if val is None or val == []:
                    data['styles'] = Style()
                else:
                    styles = ensure_iterable(val)
                    for style in styles:
                        data['styles'].add_style(style, strict=False)

            # Treat style the same way
            elif key == 'style':
                if val is None or val == []:
                    data['styles'] = Style()
                else:
                    styles = ensure_iterable(val)
                    for style in styles:
                        data['styles'].add_style(style, strict=False)

            else:
                if key not in data:
                    raise FormatError(f'Invalid format attribute {key}.')
                data[key] = val
        return data

    def _set_attributes(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    """
    For the following mutation methods, the way that we can override existing
    Format instances or create mutated copies of existing Format instancese
    has functionality that makes changing values easier and more intuitive
    when provided as keyword arguments.

    If an empty list is passed in for the styles, or None, we assume the
    user wants to remove the styles.  Otherwise, styles are applied on
    top of the currenet styles.  We also allow styles to be explicitly
    specified as True or False.  Thus, all of the following are valid:

    >>> fmt = Format(...)
    >>> fmt.including(bold=False)
    >>> fmt.including(bold=True)
    >>> fmt.including(styles='bold')
    >>> fmt.including(styles=None)
    >>> fmt.including(styles=['bold'])
    """

    def override(self, **kwargs):
        """
        Overrides the existing Format instance with the provided arguments,
        where there is flexibility in how the arguments can be supplied.
        """
        overrides = self._initialization_kwargs(**kwargs)
        self._set_attributes(**overrides)

    def copy(self, **overrides):
        """
        Creates and returns a copy of the existing Format instance with the
        provided arguments, where there is flexibility in how the arguments can
        be supplied.
        """
        init_overrides = self._initialization_kwargs(**overrides)

        # Style Required for Replace, Even if None
        init_overrides.setdefault('style', init_overrides.get('styles'))
        return replace(
            self,
            **init_overrides,
        )

    @contextlib.contextmanager
    def overriding(self, **overrides):
        """
        Temporarily overrides the Format instance with the provided arguments,
        where there is flexibility in how the arguments can be supplied.

        The original Format instance will not be mutated.

        [x] NOTE:
        --------
        For all attributes, this will override them completely, except for
        the styles attribute, which we handle differently.
        """
        original = self.__dict__.copy()
        try:
            self.override(**overrides)
            yield self
        finally:
            self._set_attributes(**original)


@dataclass
class IconFormat:

    icon: str = None
    icon_before: bool = field(default=True)
    icon_after: bool = field(default=False)
    format_with_icon: bool = field(default=True)

    @property
    def icon_location(self):
        """
        Whether or not to place the icon before the text.  Defaults to True
        if neither `icon_before` or `icon_after` are set.
        """
        if self.icon_before is None and self.icon_after is None:
            return 'before'
        elif self.icon_before is not None and self.icon_after is None:
            if self.icon_before is True:
                return 'before'
            else:
                return 'after'
        elif self.icon_after is not None and self.icon_before is None:
            if self.icon_after is True:
                return 'after'
            else:
                return 'before'
        else:
            # Both `icon_after` and `icon_before` non null.
            if self.icon_after is True and self.icon_before is True:
                return 'before'
            elif self.icon_after is True:
                return 'after'
            else:
                return 'before'

    def apply_icon(self, text):
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
        """
        return self.including(icon=icon, **kwargs)

    def without_icon(self):
        """
        Creates and returns a copy of the Format instance without an icon.
        """
        return self.including(icon=None)


@dataclass
class WrapperFormat:

    wrapper: str = None
    format_with_wrapper: bool = False

    def apply_wrapper(self, text):
        """
        [x] TODO:
        ---------
        Investigate and implement other string formatting methods for specifying
        a wrapper that can be used to format the format object.
        """
        if self.wrapper:
            return self.wrapper % text

    def add_wrapper(self, wrapper, format_with_wrapper=None):
        # Preserve Format with Wrapper if Not Specified
        format_with_wrapper = (format_with_wrapper
            if format_with_wrapper is not None else self.format_with_wrapper)
        self.override(wrapper=wrapper, format_with_wrapper=format_with_wrapper)

    def remove_wrapper(self):
        self.override(wrapper=None, format_with_wrapper=False)

    def with_wrapper(self, wrapper, format_with_wrapper=None):
        """
        Returns a copy of the Format instance with the wrapper set.
        """
        # Preserve Format with Wrapper if Not Specified
        format_with_wrapper = (format_with_wrapper
            if format_with_wrapper is not None else self.format_with_wrapper)
        return self.copy(wrapper=wrapper, format_with_wrapper=format_with_wrapper)

    def without_wrapper(self):
        """
        Returns a copy of the Format instance without a wrapper.
        """
        return self.copy(wrapper=None)


@dataclass
class Format(FormatDataClass, IconFormat, WrapperFormat):

    color: typing.Union[Color, str] = field(default=None)
    styles: typing.List[typing.Union[Style, str, int]] = field(default_factory=list)
    highlight: typing.Union[Color, str] = field(default=None)
    style: InitVar[typing.Any] = None
    depth: InitVar[int] = None  # Required for Settings to Avoid Circular Import

    def __post_init__(self, style, depth):

        FormatDataClass.__post_init__(self)

        if self.color and not isinstance(self.color, Color):
            self.color = Color(self.color, depth=depth)

        if self.highlight and not isinstance(self.highlight, Color):
            self.highlight = Highlight(self.highlight, depth=depth)

        if style and not self.styles:
            if isinstance(style, Style):
                self.styles = Style
            else:
                self.styles = ensure_iterable(style, coercion=tuple, force_coerce=True)

        if not isinstance(self.styles, Style):
            self.styles = self.styles or []
            self.styles = ensure_iterable(self.styles, coercion=tuple, force_coerce=True)
            self.styles = Style(*self.styles)

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
        if text is None:
            raise FormatError('Cannot format null text.')

        text = safe_text(text)

        with self.overriding(**overrides):
            # Apply icon and wrapper before and/or after formatting depending
            # on values of `format_with_wrapper` and `format_with_icon`.
            wrapper_bounds = format_bounds(self.wrapper, self.format_with_wrapper, self.apply_wrapper)
            icon_bounds = format_bounds(self.icon, self.format_with_icon, self.apply_icon)
            text = icon_bounds(wrapper_bounds(self._format))(text)

        return text

    def _format(self, text):
        if self.color:
            text = self.color(text)
        if self.highlight:
            text = self.highlight(text)
        return self.styles(text)

    def add_style(self, style_name):
        if not self.styles.has_style(style_name):
            self.styles.add_style(style_name)

    def remove_style(self, style_name):
        if self.styles.has_style(style_name):
            self.styles.remove_style(style_name)
