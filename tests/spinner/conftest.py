import pytest

from termx import SpinnerStates
from termx.core.spinner.models import LineItem


@pytest.fixture
def make_line_item():
    def _make_line_item(indent=0, state=SpinnerStates.NOTSET, options=None):
        return LineItem(
            "Test Line",
            indent=indent,
            state=state,
            options=options
        )
    return _make_line_item
