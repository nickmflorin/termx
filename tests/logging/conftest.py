import logging
import pytest

from termx import colors
from termx.termx.formatting import Format


level = 'info'
name = 'test-logger'


def _make_record(message=None, extra=None):
    extra = extra or {}
    record = logging.makeLogRecord({
        "levelname": level.upper(),
        "name": "name",
        "msg": message or "Test Message",
    })
    for key, val in extra.items():
        setattr(record, key, val)
    return record


@pytest.fixture
def make_mock_object():

    class MockObj(object):
        def __init__(self, **kwargs):
            for key, val in kwargs.items():
                setattr(self, key, val)

    def _make_mock_object(data):
        kwargs = {}
        for key, val in data.items():
            if isinstance(val, dict):
                kwargs[key] = _make_mock_object(val)
            else:
                kwargs[key] = val
        return MockObj(**kwargs)

    return _make_mock_object


@pytest.fixture
def make_record():
    return _make_record


@pytest.fixture
def null_record_callable():
    def _callable(record):
        return None
    return _callable


@pytest.fixture
def level_callable():
    def _callable(record):
        return record.levelname
    return _callable


@pytest.fixture
def record():
    return _make_record(extra={
        'color_string': 'blue',
        'color': colors.red,
        'format': Format(colors.blue, colors.bold)
    })
