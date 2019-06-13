import plumbum
from plumbum import colors

from termx.utils import ensure_list
from termx.formatting import Format
from termx.formatting.exceptions import InvalidColor

from termx.logging.exceptions import InvalidCallable


def get_obj_attribute(obj, param):
    """
    Given an object, returns the parameter for that object if it exists.  The
    parameter can be nested, by including "." to separate the nesting of objects.

    For example, get_obj_attribute(test_obj, 'fruits.apple.name') would get
    the 'fruits' object off of `test_obj`, then the 'apple' object and then
    the 'name' attribute on the 'apple' object.
    """
    if "." in param:
        parts = param.split(".")
        if len(parts) > 1:
            if isinstance(obj, dict) and parts[0] in obj:
                return get_obj_attribute(obj[parts[0]], '.'.join(parts[1:]))

            if hasattr(obj, parts[0]):
                nested_obj = getattr(obj, parts[0])
                return get_obj_attribute(nested_obj, '.'.join(parts[1:]))
            else:
                return None
        else:
            if isinstance(obj, dict) and parts[0] in obj:
                return obj[parts[0]]
            elif hasattr(obj, parts[0]):
                return getattr(obj, parts[0])
    else:
        if hasattr(obj, param):
            return getattr(obj, param)
        return None


def get_record_attribute(record, params):
    """
    Given an "attribute" set as `params` and a record, finds the value for
    each attr in the set, returning the first non-null value on the record.

    The parameter `params` can be an iterable or a single string, and can
    reference nested or top level dictionary/object attributes separated
    by '.'.

    >>> record = {'child': {'grandchild': {'age': 10}}, 'name': 'Jack'}
    >>> get_record_attribute(record, ['child.grandchild.name', 'child.name'])
    >>> 'Jack'
    """
    # TODO: Need to catch more singletons here.
    params = ensure_list(params)
    params = ["%s" % param for param in params]

    # Here, each param can be something like "context.index", or "index"
    # Higher priority is given to less deeply nested versions.
    for param in params:
        value = get_obj_attribute(record, param)
        if value is not None:
            return value
    return None


def get_callable_value(record, callwith):
    if not callable(callwith):
        raise ValueError('Value must be a callable.')
    try:
        return callwith(record)
    except TypeError as e:
        raise InvalidCallable(callwith, additional=str(e))


def get_value(record, value=None, attrs=None):
    """
    Given a record object and a value, returns an appropriate loggable value.
    The value can be:

    (1) A constant string -> Will be returned
    (2) A string representing nested or non-nested attributes on record object
    (3) A record callable that returns (1)

    The value CANNOT be:
    (4) A record callable that returns (2).  See discussion below.

    [x] NOTE:
    --------
    This method cannot be as "intelligent" as `get_format()`, in that we must
    tell it whether or not the information being passed in represents a
    string value/callable (`value`) or attributes on the record.

    This is because if we pass in attributes ['level.name'], it cannot tell if
    that is supposed to be the constant string output or attributes on the record.

    This would lead to us having created loggable items when `level.name` is
    missing.
    """
    if not value and not attrs:
        raise ValueError('Must specify `value` or `attrs`.')

    # Get value by calling callable on record.  Will raise an exception
    # if the callable is invalid.  Recursively use get_value() just in case
    # the callable returns a string representing attributes on the record.
    if value:
        if callable(value):
            value = get_callable_value(record, value)

            # We cannot call this recursively since there is no way to differentiate
            # between string and attributes, but if it is a valid attribute, we want
            # to return that.
            attribute_value = get_record_attribute(record, value)
            if attribute_value:
                return attribute_value

            # Will raise ValueError if value is None.
            if value is not None:
                return get_value(record, value=value)
        else:
            # Constant String Value
            return value
    else:
        attribute_value = get_record_attribute(record, attrs)

        # Attribute Value Can be Callable
        if attribute_value:
            return get_value(record, value=attribute_value)

        # Attribute is not on the record instance, we want to return None so
        # loggable element isn't created.
        return None


def get_format(record, value):
    """
    Given a record object and a value, returns an appropriate Format object.
    The value can be:

    (1) A string color ("blue")
    (2) A plumbum color (colors.blue)
    (3) A format object (Format(colors.blue, colors.bold))
    (4) A record callable returning any of the above
    """
    if callable(value):
        # Test if it is a Artsylogger Format object
        if isinstance(value, Format):
            return value
        # Test if it is a Plumbum Colors object
        elif type(value) == plumbum.colorlib.styles.ANSIStyle:
            return Format(value)

        # Get value by calling callable on record.  Will raise an exception
        # if the callable is invalid.

        # [x] TODO:
        # This part needs some work...

        # This enforces that the first callable operates on a record
        # which might return a second callble (a formatting function) that operates
        # on a string.  We should allow a callable that operates on a string
        # to be passed in.
        else:
            # This enforces that the first callable operates on a record first.
            try:
                # The callable might not be a record callable, but something
                # from an enum that operates on a string.
                value = get_callable_value(record, value)
            except InvalidCallable:
                return value

            # We can have a callable that is not an instance of Format but
            # still formats the text, particularly for the case of Enums.
            # We should probably find a more concrete way of doing this.
            if callable(value):
                if type(value) == plumbum.colorlib.styles.ANSIStyle:
                    return Format(value)
                return value

            return get_format(record, value)

    elif isinstance(value, str):

        # Test if it is a Plumbum Colors compatible string
        if hasattr(colors, value):
            value = getattr(colors, value)
            return Format(value)

        # Must be a string representing attributes on the record, the value
        # might either be a string color, color or Format object.  Maybe even
        # a callable, but that is why we recursively call get_format() again.
        else:
            val = get_record_attribute(record, value)
            if val is not None:
                return get_format(record, val)
            return None

    else:
        raise InvalidColor(value)
