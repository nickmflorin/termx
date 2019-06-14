from termx.formatting import Colors, Format
from termx.colorlib import style


def test_style():

    sty = style('bold')
    formatted = sty('foo')
    print(formatted)
