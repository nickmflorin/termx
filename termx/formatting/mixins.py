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
