from simple_settings import settings

from termx.config.doc import ConfigDoc
from termx.colorlib import color


def test_override_top_level(override_settings):
    override_settings({'COLOR_DEPTH': 24})
    assert settings.COLOR_DEPTH == 24


def test_override_color_value(override_settings):

    # Overriding COLOR_DEPTH not for testing purposes, but to make sure we use
    # the same COLOR_DEPTH in tests.
    override_settings({'COLOR_DEPTH': 256})
    override_settings({'COLORS': {'GREEN': 'BLUE'}})

    # Overriding Should Maintain ConfigDoc Instances
    assert isinstance(settings.COLORS, ConfigDoc)
    assert isinstance(settings.COLORS.GREEN, color)

    value = settings.COLORS.GREEN('foo')
    assert value == '\x1b[38;5;4mfoo\x1b[0m'

    # Make Sure Existing Values Still Present
    assert hasattr(settings.COLORS, 'RED')
    value = settings.COLORS.RED('foo')
    assert value == '\x1b[38;5;167mfoo\x1b[0m'
