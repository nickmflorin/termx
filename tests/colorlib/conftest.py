import pytest

from termx.spinner.models import LineItem, SpinnerStates


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
