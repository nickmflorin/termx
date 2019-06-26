import re


class ConditionalString(str):

    def __new__(cls, *args, sep=" ", end_with='.'):
        value = str.__new__(cls, sep.join(list(args)))

        setattr(value, 'components', list(args))
        setattr(value, 'sep', sep)
        setattr(value, 'end_with', end_with)

        return value

    @classmethod
    def get_conditionals(cls, arg):
        regex = r"\{(.*?)\}"
        return re.findall(regex, arg)

    def formatted(self, *args, **kwargs):
        flattened = []
        for arg in self.components:
            conditionals = self.get_conditionals(arg)
            if conditionals:
                if all([conditional in kwargs for conditional in conditionals]):
                    flattened.append(arg.format(**kwargs))
            else:
                flattened.append(arg.format(**kwargs))
        return flattened

    @property
    def indentation(self):
        return self.space_before * " "

    def format(self, **kwargs):
        formatted = self.formatted(**kwargs)
        if formatted:
            formatted = self.sep.join(formatted)
            if self.end_with:
                formatted = "%s%s" % (formatted, self.end_with)
            return formatted
        return ""

    def __add__(self, other):
        comps = self.components + other.components
        return ConditionalString(*comps, sep=self.sep, end_with=self.end_with)


def humanize_list(value, callback=str, conjunction='and', oxford_comma=True):
    """
    Turns an interable list into a human readable string.
    >>> list = ['First', 'Second', 'Third', 'fourth']
    >>> humanize_list(list)
    u'First, Second, Third, and fourth'
    >>> humanize_list(list, conjunction='or')
    u'First, Second, Third, or fourth'
    """

    num = len(value)
    if num == 0:
        return ""
    elif num == 1:
        return callback(value[0])
    s = u", ".join(map(callback, value[:num - 1]))
    if len(value) >= 3 and oxford_comma is True:
        s += ","
    return "%s %s %s" % (s, conjunction, callback(value[num - 1]))


def string_format_tuple(value):
    """
    Recursively formats a tuple and nested tuples into string format.
    """
    value = list(value)
    formatted = []

    for item in value:
        if isinstance(item, tuple):
            formatted.append(string_format_tuple(item))
        else:
            formatted.append("%s" % item)

    return '(' + ', '.join(formatted) + ')'
