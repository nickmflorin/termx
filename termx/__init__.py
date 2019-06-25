"""
[!] VERY IMPORTANT
-----------------
Since we are using termx locally with other repositories, we have to define
settings lazily, otherwise, the other packages that are using simple_settings
will have settings conglomerated with termx's simple settings.

In order to do that, we will set the termx settings object here lazily, so that
imports are done as:

>>> from termx import settings

instead of

>>> from simple_settings import settings

Note that we still cannot termx.config from certain modules because of circular
import issues, so we could not switch over to using config instead of simple_settings
settings object.  However, this is probably the more straight forward way of
doing this.
"""

from .core import terminal, spinner, formatting, colorlib  # noqa
from .config import settings


def configure_settings(*args, **kwargs):
    """
    Updates the settings object (i.e. uses the .configure method of simple_settings)
    but does so in a way that maintains ConfigDoc objects and updates nested
    objects/settings in a non-destructive way.

    Called Externally, Convenience Import

    >>> from termx import settings
    >>> settings.configure(...)

    or

    >>> from termx import configure_settings
    >>> configure_settings(...)
    """
    settings.configure(*args, **kwargs)
