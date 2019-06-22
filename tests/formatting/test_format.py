from termx import Format, color
from termx.config import config


def test_format_with_color(override_settings):
    override_settings({'COLOR_DEPTH': 256, 'COLORS': {'GREEN': 'BLUE'}})

    def initialize_with_string():
        fmt = Format(color='blue')
        value = fmt.color('foo')
        import ipdb; ipdb.set_trace()
        assert value == '\x1b[34mfoo\x1b[0m'

    def initialize_with_color():
        fmt = Format(color=color('blue'))
        value = fmt.color('foo')
        assert value == '\x1b[34mfoo\x1b[0m'

    def initialize_with_hex():
        fmt = Format(color='#000000')
        value = fmt.color('foo')
        assert value == '\x1b[38;2;0;0;0mfoo\x1b[0m'

    initialize_with_string()
    initialize_with_color()
    # initialize_with_hex()


def test_format_with_style():

    def initialize_with_string():
        fmt = Format(color='black', styles=['bold', 'underline'])
        value = fmt('foo')
        assert value == '\x1b[1;4m\x1b[30mfoo\x1b[0m\x1b[0m'

    def initialize_with_code():
        fmt = Format(color='black', styles=[1, 4])
        value = fmt('foo')
        assert value == '\x1b[1;4m\x1b[30mfoo\x1b[0m\x1b[0m'

    initialize_with_string()
    initialize_with_code()


def test_wraps_text():

    # Initializing With Wrapper
    fmt = Format(color='blue', wrapper="[%s]")
    value = fmt('foo')
    assert value == "[\x1b[34mfoo\x1b[0m]"

    # Initializing With Wrapper & Formatting With Wrapper
    fmt = Format(color='blue', wrapper="[%s]", format_with_wrapper=True)
    value = fmt('foo')
    assert value == '\x1b[34m[foo]\x1b[0m'

    # Calling with Wrapper
    fmt = Format(color='blue')
    value = fmt('bar', wrapper="[%s]")
    assert value == "[\x1b[34mbar\x1b[0m]"
    assert fmt.wrapper is None

    # Calling with Wrapper and Format w Wrapper
    fmt = Format(color='blue')
    value = fmt('bar', wrapper="[%s]", format_with_wrapper=True)
    assert value == '\x1b[34m[bar]\x1b[0m'
    assert fmt.wrapper is None
    assert fmt.format_with_wrapper is False


def test_decorates():
    """
    [x] Note:
    --------
    Since we are now generating these sequences on our own and separating styles
    from colors, we will not have the combined ANSII sequences that we would
    see with Plumbum (since Plumbum treated colors.bold and colors.blue as
    the same operation).

    [!] We should see if there is a way for us to do that, since it makes the
    ANSII output a lot cleaner.

    [x] Note:
    --------
    We also need to be cognizant of how we add certain overrides on __call__
    and how that applies with styles and mutable lists.
    """

    # Test Decorates
    fmt = Format(color='blue', styles=['bold'])
    value = fmt('foo')

    # assert value == '\x1b[1;34mfoo\x1b[22;39m'
    assert value == '\x1b[1m\x1b[34mfoo\x1b[0m\x1b[0m'

    # Test Add/Remove Decoration on Call
    value = fmt('foo', styles=['underline', 'bold'])
    assert value == '\x1b[1;4m\x1b[34mfoo\x1b[0m\x1b[0m'


def test_with_icon():

    # Test Decorates
    fmt = Format(color='blue', styles=['bold'], icon="[i]", icon_after=True)
    value = fmt('foo')
    assert value == '\x1b[1m\x1b[34mfoo [i]\x1b[0m\x1b[0m'

    # Format With Icon on Call
    fmt = Format(color='blue', styles=['bold'], icon="[i]", icon_before=True)
    value = fmt('foo', format_with_icon=False)
    assert value == '[i] \x1b[1m\x1b[34mfoo\x1b[0m\x1b[0m'
    assert fmt.format_with_icon is True
