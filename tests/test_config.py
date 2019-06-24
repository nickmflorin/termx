from simple_settings import settings

from termx.colorlib import color
from termx.core.formatting import Format

from termx.config import config
from termx.config.doc import ConfigDoc


def test_config_updates_settings(override_settings):
    override_settings({'foo': 'bar'})
    assert settings.FOO == 'bar'


def test_config_updates(override_settings):
    override_settings({'foo': 'bar'})
    assert config.FOO == 'bar'


def test_access_case_insensitive(override_settings):
    override_settings({'COLORS': {'GREEN': 'BLUE'}})

    assert getattr(config, 'colors', None) is not None
    assert getattr(config.colors, 'green', None) is not None
    assert isinstance(config.colors.green, color)

    override_settings({'color_depth': 24})
    assert settings.COLOR_DEPTH == 24
    assert config.COLOR_DEPTH == 24


def test_override_color_value(override_settings):
    """
    [x] TODO:
    --------
    These tests rely on the assumption that certain values we set in our default
    config file are there, since it is imported by test.py.  We should set
    constant test values.
    """

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


def test_override_format_value(override_settings):
    """
    [x] TODO:
    --------
    These tests rely on the assumption that certain values we set in our default
    config file are there, since it is imported by test.py.  We should set
    constant test values.
    """
    override_settings({'COLOR_DEPTH': 256})

    # Test Override as Dict
    override_settings({'FORMATS': {'INFO': {'COLOR': 'red', 'ICON': '[?]', 'STYLE': 'UNDERLINE'}}})

    fmt = config.formats.info

    assert fmt.color.ansi_codes == [38, 5, 1]
    assert fmt.icon == '[?]'
    assert fmt.styles.ansi_codes == (4, )

    # Test Override as Format
    override_settings({'FORMATS': {'INFO': Format(color='blue', icon="[?]", styles=['underline'])}})

    fmt = config.formats.info

    assert fmt.color.ansi_codes == [38, 5, 4]
    assert fmt.icon == '[?]'
    assert fmt.styles.ansi_codes == (4, )
