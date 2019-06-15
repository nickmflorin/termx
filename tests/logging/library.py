from termx import Format, color
from termx.logging import Lines, Line, Label, Segment


def test_label(make_mock_object, make_record, null_record_callable):

    obj = make_mock_object({'value1': {'value1': 'foo', 'value2': 'bar'}, 'value2': 'baz'})
    record = make_record(extra={'object': obj})

    label = Label(
        value="Proxy",
        format=Format(color='black', styles='bold'),
        delimiter=":",
    )(record)
    assert label == '\x1b[1;30mProxy\x1b[22;39m:'

    label = Label(
        attrs="object.value2",
        format=Format(color='black', styles='bold'),
        delimiter=":",
    )(record)
    assert label == '\x1b[1;30mbaz\x1b[22;39m:'

    label = Label(
        attrs="object.value4",
        format=Format(color='black', styles='bold'),
        delimiter=":",
    )(record)
    assert label == ''


def test_lines(make_mock_object, make_record, null_record_callable):
    """
    For many of these tests, there are too many different combinations to write
    a descriptive test function and test for - we will try to cover as many
    as possible by grouping some related tests with different formations and
    combinations in the same test method.

    For now, we will take some typical formatting setups from projects using
    artsylogger.
    """
    def get_record_message(record):
        if hasattr(record, 'object') and hasattr(record.object, 'exception'):
            return getattr(record.object.exception, 'message', None)
        return record.msg

    def get_record_status_code(record):
        if hasattr(record, 'object') and hasattr(record.object, 'exception'):
            return getattr(record.object.exception, 'status_code', None)

    def get_message_formatter(record):
        return Format(color='black', styles='underline')

    obj = make_mock_object({
        'exception': {
            'status_code': 200,
            'message': 'Timeout Error'
        }
    })
    record = make_record(extra={
        'object': obj,
        'other': 'Other Message'
    })

    lines = Lines(
        Line(
            Segment(
                value=get_record_message,
                format=get_message_formatter,
            ),
            prefix=Format(color=color('Grey58'))(">"),
        ),
        Line(
            Segment(
                value=get_record_status_code,
                format=Format(color=color('Red'), styles='bold')
            ),
            prefix=Format(color=color('Grey58'))(">"),
        ),
        Line(
            Segment(
                attrs="other",
                format=Format(color=color('Grey30'), styles='bold'),
            ),
            prefix=Format(color=color('Grey58'))(">"),
        ),
        indent=1,
    )

    assert lines(record) == [
        ' \x1b[38;5;246m>\x1b[39m \x1b[4;30mTimeout Error\x1b[24;39m',
        ' \x1b[38;5;246m>\x1b[39m \x1b[1;31m200\x1b[22;39m',
        ' \x1b[38;5;246m>\x1b[39m \x1b[1;38;5;239mOther Message\x1b[22;39m'
    ]

    # Make Sure Invalid Lines Removed
    obj = make_mock_object({
        'exception': {
            'status_code': 200,
        }
    })
    record = make_record(extra={
        'object': obj,
    })

    assert lines(record) == [
        ' \x1b[38;5;246m>\x1b[39m \x1b[1;31m200\x1b[22;39m',
    ]
