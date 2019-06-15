"""
This module is going to lay the groundwork for termx's custom colorlib, which
we are doing partially for fun (since there are alternatives out there) but
also for customization purposes, so that we can more easily leverage a colorlib
that works for both ANSI cases and in the curses library.

[x] TODO:
--------
We might want to make our own color class, similar to plumbum's AnsiStyles
class.

[x] IMPORTANT
------------
Note the difference and decide between the use of \x1b and \033

Packages to Consider
--------------------
pip install ansicolors

>>> green('green on black', bg='black', style='underline')
>>> red('very important', style='bold+underline')
>>> color('nice color', 'white', '#8a2be2')

Plumbum
-------
Plumbum colors.fg(), colors.bg() or colors.attr returns an object
<ANSIStyle: Background Green>.

The following properties/methods might be useful:
(1) from_ansi
(2) from_color
(3) full
(4) wrap
(5) attributes
(6) fg
(7) bg
(8) from_ansi
(9) from_color
(10) add_ansi
(11) ansi_codes >>> [38, 2, 239, 239, 239]
(12) ansi_sequence >>> '\x1b[38;2;239;239;239m'
(13) attribute_names
(14) attributes
(15) string_contains_colors

"""
from .colour import color  # noqa
from .style import style  # noqa
