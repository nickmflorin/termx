"""
For the termx module, we want to expose the config object that can be used
to configure the Colors, Formats, Styles and Icons externally by package users.

We also want to expose the Colors, Formats, Icons and Styles objects that are
configurable.

In Another Package:
------------------
>>> from termx.config import config
>>> config({'Colors': {'BLUE': ...}})

>>> from termx import Colors
>>> Colors.BLUE('Test Message')

The configurable objects all lazily import the Format, color and style objects
in lower levels of the module to import circular import issues.

Internal to Package:
-------------------
Inside the termx package, we still have to import Colors, Formats, Icons and
Styles from the config object:

>>> from termx.config import Colors
"""

# We Have to Import to Initialize
from termx.config import config  # noqa

from termx.colorlib import *  # noqa

from .terminal import *  # noqa
from .spinner import *  # noqa
from .formatting import *  # noqa

# Formats, Text, Colors, Styles, Icons = STYLE_CONFIG({})

__NAME__ = 'termx'
__FORMAL_NAME__ = __NAME__.title()
__VERSION__ = (0, 0, 2, 'alpha', 0)

# global Colors
# Colors = _Colors

# global Styles
# Styles = _Styles

# global Formats
# Formats = _Formats

# global Icons
# Icons = _Icons


# def configure(data):
#     """
#     Configures the global module styling properties.

#     [x] IMPORTANT:
#     -------------
#     In order to apply custom configuration, the configure method must be
#     called at the top level, before any of the modules are imported:

#     >>> import termx
#     >>> termx.configure({...})

#     >>> from termx import Colors
#     >>> Colors.GREEN('Test Message')
#     """
#     global Colors
#     global Styles
#     global Formats
#     global Icons

#     Formats, Colors, Styles, Icons = config(data)
