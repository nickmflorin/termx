from termx.utils import ensure_iterable

from .base import formatter
from .exceptions import InvalidStyle


class StyleMeta(type):

    def __init__(cls, name, bases, nmspc):
        super(StyleMeta, cls).__init__(name, bases, nmspc)
        cls.SUPPORTED_CODES = [
            sp[1] for sp in cls.SUPPORTED
        ]
        cls.SUPPORTED_STYLES = [
            sp[0] for sp in cls.SUPPORTED
        ]

    def __getattr__(cls, name):
        print('Getting Class Attr %s' % name)
        try:
            code = cls.code_for(name)
        except InvalidStyle:
            return super(StyleMeta, cls).__getattr__(name)
        else:
            return cls(code)


class style(formatter, metaclass=StyleMeta):

    """
    Useful Resources
    ----------------
    https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences
    """
    SUPPORTED = [
        ('bold', 1),
        ('faint', 2),
        ('italic', 3),
        ('underline', 4),
        ('slow_blink', 5),
        ('rapid_blink', 6),
        ('conceal', 8),
        ('crossed_out', 9),
        ('encircle', 52),
        ('overline', 53),
    ]

    def __init__(self, *args):
        self._styles = self._set_styles(
            ensure_iterable(args, coercion=tuple, force_coerce=True))

    @property
    def styles(self):
        return self._styles

    # NOTE: This kind of makes the use of the ansi_codes property useless.
    @styles.setter
    def styles(self, value):
        self._styles = self._set_styles(value)

    def _set_styles(self, styles):
        """
        Converts all styles that might be either string names or codes to
        codes and ensures they are supported.
        """
        supported_styles = []
        for st in styles:
            code = self.to_code_safe(st)
            supported_styles.append(code)
        return tuple(supported_styles)

    def __call__(self, *args):
        """
        Checking whether or not the text is even supplied as an argument allows
        us to do the following:

        Option 1:
        --------
        >>> st = style('bold')
        >>> st('Test Message')

        Option 2: (No Args)
        ---------
        >>> st = st.bold()
        >>> st('Test Message')

        Using this in conjunction with the overridden __getattr__ method allows
        us to chain together styles through the application of methods, and to
        apply the chain by supplying text:

        >>> st = style.bold().underline()
        >>> st('Test Message')

        >>> styled = style.bold().underline("TEST")

        All together, this makes for a convenient colorlib API interface.
        """
        if len(args) == 0:
            return self

        value = self._formatter % ("%s" % args[0])
        return value

    def __getattr__(self, name):
        """
        Not only do we want to access style attributes by name as methods on the
        class level, but we want to be able to do this on the instance level to
        either (1) Mutate the Existing Style or (2) Apply Additional Style w/o
        Mutating Existing Style

        (1) Mutating Existing Style Obj
        -------------
        >>> st = style('bold')
        >>> st('TEST')  ===>  Outputs Bold
        >>> st.underline()
        >>> st('TEST')  ===> Ouputs Bold & Underlined

        (2) Applying Unmutated Style w/ Additional Temporary Style
        -------------
        >>> st = style('bold')
        >>> st('TEST')  ===>  Outputs Bold
        >>> st.underline("TEST")  ===> Ouputs Bold & Underlined
        >>> st('TEST')  ===>  Outputs Bold

        An exception will be raised when the style is added if it already exists
        on the object.
        """
        try:
            code = self.code_for(name)
        except InvalidStyle:
            return super(style, self).__getattr__(name)
        else:
            def lazy_style(*args):
                """
                This is where the attribute received can either act as a mutated
                style object or apply the current style to text with an additional
                style.
                """
                if len(args) == 0:
                    self.add_style(code)
                    return self

                mutated_codes = self.styles[:] + [code]
                return style(*mutated_codes)(args[0])

            return lazy_style

    @property
    def ansi_codes(self):
        return self.styles

    @classmethod
    def code_for(cls, style_name):
        if style_name not in cls.SUPPORTED_STYLES:
            raise InvalidStyle(style_name)
        return [st[1] for st in cls.SUPPORTED if st[0] == style_name][0]

    @classmethod
    def name_for(cls, code):
        if code not in cls.SUPPORTED_CODES:
            raise InvalidStyle(code)
        return [st[0] for st in cls.SUPPORTED if st[1] == code][0]

    @classmethod
    def supported(cls, style_or_code):
        return style_or_code in cls.SUPPORTED_STYLES + cls.SUPPORTED_CODES

    def to_code_safe(self, style_or_code):
        """
        For purposes of checking whether or not a style exists or doesn't exist
        in the object, we want the ability to pass in string styles or integer
        codes.

        We also want to raise an exception if it is not even supported.

        This method makes sure that either the string name or code is supported
        and returns the supported code if it is.
        """
        try:
            code = int(style_or_code)
        except ValueError:
            # Will Raise Exception if Unsupported
            return self.code_for(style_or_code)
        else:
            if code not in self.SUPPORTED_CODES:
                raise InvalidStyle(code)
            return code

    def to_name_safe(self, style_or_code):
        """
        For purposes of checking whether or not a style exists or doesn't exist
        in the object, we want the ability to pass in string styles or integer
        codes.

        We also want to raise an exception if it is not even supported.

        This method makes sure that either the string name or code is supported
        and returns the supported name if it is.
        """
        try:
            style_or_code = int(style_or_code)
        except ValueError:
            if style_or_code not in self.SUPPORTED_STYLES:
                raise InvalidStyle(style_or_code)
            return style_or_code
        else:
            # Will Raise Exception if Unsupported
            return self.name_for(style_or_code)

    def has_style(self, style_or_code):
        code = self.to_code_safe(style_or_code)
        return code in self.styles

    def add_styles(self, *styles, strict=True):
        for st in styles:
            self.add_style(st, strict=strict)

    def remove_styles(self, *styles, strict=True):
        for st in styles:
            self.remove_style(st, strict=strict)

    def add_style(self, style_or_code, strict=True):
        """
        Raises an exception if the style is not supported or already exists.
        """
        if self.has_style(style_or_code):
            name = self.to_name_safe(style_or_code)
            if strict:
                raise ValueError('Style %s already exists in object.' % name)
        else:
            code = self.code_for(name)
            self.styles = self.styles + (code, )

    def remove_style(self, style_or_code, strict=True):
        """
        Raises an exception if the style is not supported or it does not exist.
        """
        if not self.has_style(style_or_code):
            name = self.to_name_safe(style_or_code)
            if strict:
                raise ValueError('Style %s does not exist in object.' % name)
        else:
            code = self.code_for(name)
            styles = list(self._styles)
            styles.remove(code)
            self.styles = tuple(styles)

    def clear(self):
        self.styles = ()

    def clear_decoration(self):
        """
        [x] TODO:
        --------
        Be more selective about which styles are related to text decoration.
        """
        self.styles = ()
