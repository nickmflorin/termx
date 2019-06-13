from termx import colors
from termx.formatting import Format
from termx.logging.utils import get_value, get_format


def test_get_value_invalid_attrs(make_mock_object, make_record):
    obj = make_mock_object({'foo': 'bar', 'fooey': {'fooz': 'barz'}})
    record = make_record(extra={'baz': obj})

    value = get_value(record, attrs="baz.fooey.bar")
    assert value is None


def test_get_value_from_attrs(make_mock_object, make_record):
    obj = make_mock_object({'foo': 'bar', 'fooey': {'fooz': 'barz'}})
    record = make_record(extra={'baz': obj})

    value = get_value(record, attrs="baz.foo")
    assert value == 'bar'


def test_get_value_from_attrs_callable(make_mock_object, make_record):

    def record_callable(record):
        return record.foo

    # Callable Can Also be Referenced as Nested Record Attribute
    obj = make_mock_object({'fooey': {'fooz': record_callable}})
    record = make_record(extra={'baz': obj, 'foo': 'bar'})

    value = get_value(record, attrs='baz.fooey.fooz')
    assert value == 'bar'


def test_get_value_from_value(record):
    value = get_value(record, value="Value")
    assert value == 'Value'


def test_get_value_from_callable(make_mock_object, make_record):

    def record_callable(record):
        return record.foo

    # Callable Can be Direct Value
    record = make_record(extra={'foo': 'bar'})
    value = get_value(record, value=record_callable)
    assert value == 'bar'


def test_get_format_from_color_string(record):
    format = get_format(record, "blue")
    assert format == Format(colors.blue)


def test_get_format_from_color(record):
    format = get_format(record, colors.red)
    assert format == Format(colors.red)


def test_get_format_from_format(record):
    format = get_format(record, Format(colors.blue, colors.bold))
    assert format == Format(colors.blue, colors.bold)


def test_get_format_from_callable(record):

    def record_callable(record):
        return record.color_string

    format = get_format(record, record_callable)
    assert format == Format(colors.blue)

    def record_callable(record):
        return record.color

    format = get_format(record, record_callable)
    assert format == Format(colors.red)

    def record_callable(record):
        return record.format

    format = get_format(record, record_callable)
    assert format == Format(colors.blue, colors.bold)
