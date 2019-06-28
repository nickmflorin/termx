import pytest
from termx import settings


@pytest.fixture
def override_settings():
    """
    Use config to update settings instead of settings.configure() because config
    handles the recursion in the nested style fields.
    """
    return settings.override
