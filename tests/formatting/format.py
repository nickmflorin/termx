from termx import colors
from termx.formatting import Format


def test_wraps_text():

    # Initializing With Wrapper
    fmt = Format(colors.blue, wrapper="[%s]")
    value = fmt('Test Value')
    assert value == "[\x1b[34mTest Value\x1b[39m]"

    # Initializing With Wrapper & Formatting With Wrapper
    fmt = Format(colors.blue, wrapper="[%s]", format_with_wrapper=True)
    value = fmt('Test Value')
    assert value == '\x1b[34m[Test Value]\x1b[39m'

    # Calling with Wrapper
    fmt = Format(colors.blue)
    value = fmt('Test Value', wrapper="[%s]")
    assert value == "[\x1b[34mTest Value\x1b[39m]"
    assert fmt.wrapper is None

    # Calling with Wrapper and Format w Wrapper
    fmt = Format(colors.blue)
    value = fmt('Test Value', wrapper="[%s]", format_with_wrapper=True)
    assert value == '\x1b[34m[Test Value]\x1b[39m'
    assert fmt.wrapper is None
    assert fmt.format_with_wrapper is False


def test_decorates():

    # Test Decorates
    fmt = Format(colors.blue, colors.bold)
    value = fmt('Test Value')
    assert value == '\x1b[1;34mTest Value\x1b[22;39m'

    # Test Add/Remove Decoration on Call
    value = fmt('Test Value', underline=True, bold=False)
    assert value == '\x1b[4;34mTest Value\x1b[24;39m'
    assert fmt.is_underline is False
    assert fmt.is_bold is True


def test_iconizes():

    # Test Decorates
    fmt = Format(colors.blue, colors.bold, icon="[i]", icon_after=True)
    value = fmt('Test Value')
    assert value == '\x1b[1;34mTest Value [i]\x1b[22;39m'

    # Format With Icon on Call
    fmt = Format(colors.blue, colors.bold, icon="[i]", icon_before=True)
    value = fmt('Test Value', format_with_icon=False)
    assert value == '[i] \x1b[1;34mTest Value\x1b[22;39m'
    assert fmt.format_with_icon is True
