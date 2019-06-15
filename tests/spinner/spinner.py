from termx import Colors, Format, SpinnerStates, Spinner


def test_spinner_init():

    spinner = Spinner(color="red")
    with spinner.group('First Group') as gp:
        gp.write('First Write')
