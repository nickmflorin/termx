from termx import style


def test_style():

    sty = style('bold')
    formatted = sty('foo')
    print(formatted)
