from termx import Colors, Format, SpinnerStates


def test_line_item(make_line_item):

    def with_string_label():
        pass

    def with_label():

        def with_label_color():
            pass

        def without_label_color():
            pass

        def without_icon():

            item = make_line_item(indent=0, state=SpinnerStates.WARNING, options={
                'label': True,
                'show_icon': False,
                'show_datetime': False
            })

            # Even though indent = 0, line items start off indented by 2 spaces underneath
            # the header lines.
            bullet_fmt = Format(Colors.SHADES[3])
            bullet = bullet_fmt(">")
            text_fmt = Format(Colors.SHADES[1])
            text = text_fmt("Test Line")

            label = SpinnerStates.WARNING.fmt.without_icon()(SpinnerStates.WARNING.label)

            expected = f"  {bullet} {label}: {text}"
            formatted = item.format()
            assert formatted == expected

        def with_icon():

            item = make_line_item(indent=1, state=SpinnerStates.WARNING, options={
                'label': True,
                'show_icon': True,
                'show_datetime': False
            })
            formatted = item.format()

            # Even though indent = 0, line items start off indented by 2 spaces underneath
            # the header lines.
            bullet_fmt = SpinnerStates.WARNING.fmt.apply_color
            bullet = bullet_fmt("✘")
            text_fmt = Format(Colors.SHADES[2])
            text = text_fmt("Test Line")

            label = SpinnerStates.WARNING.fmt.without_icon()(SpinnerStates.WARNING.label)

            expected = f"    {bullet} {label}: {text}"
            formatted = item.format()
            assert formatted == expected

        def with_icon_color():

            item = make_line_item(indent=1, state=SpinnerStates.WARNING, options={
                'label': True,
                'show_icon': True,
                'color_icon': False,
                'show_datetime': False
            })

            formatted = item.format()

            # Even though indent = 0, line items start off indented by 2 spaces underneath
            # the header lines.
            bullet_fmt = Format(Colors.SHADES[4])
            bullet = bullet_fmt("✘")
            text_fmt = Format(Colors.SHADES[2])
            text = text_fmt("Test Line")

            label = SpinnerStates.WARNING.fmt.without_icon()(SpinnerStates.WARNING.label)

            expected = f"    {bullet} {label}: {text}"
            formatted = item.format()
            assert formatted == expected

        with_label_color()
        without_label_color()
        without_icon()
        with_icon()
        with_icon_color()

    def without_label():

        def without_icon():
            pass

        def with_icon():
            pass

        def with_icon_color():
            pass

        without_icon()
        with_icon()
        with_icon_color()

    with_label()
    without_label()
