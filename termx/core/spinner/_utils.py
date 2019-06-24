from termx.ext.compat import ( # noqa
    PY2, basestring, builtin_str, bytes, iteritems, str, safe_text, to_unicode,
    ENCODING)


def get_frames(spinner):
    """
    [x] NOTE:
    --------
    We don't really have to worry about this method for the time being, since
    we are using a default spinner for all cases.  Although, if we expand
    to be like Yaspin, we will need this functionality expanded.

    type: (base_spinner.Spinner, bool) -> Union[str, List]
    """
    if spinner.frames:
        if isinstance(spinner.frames, basestring):
            frames = spinner.frames
            if PY2:
                frames = to_unicode(spinner.frames)
            return frames

        # TODO: Support Any Type That Supports Iterable
        if isinstance(spinner.frames, (list, tuple)):
            frames = spinner.frames
            if isinstance(spinner.frames[0], bytes):
                frames = [to_unicode(frame) for frame in spinner.frames]
            return frames

    else:
        raise ValueError("{0!r}: No Frames Found for Spinner".format(spinner))


def shaded_level(level, bold=False, dark_limit=0, light_limit=None, gradient=1):
    """
    [x] TODO:
    --------
    It is not a good idea right now to use the `gradient` parameter, because the
    discretized shades are not extensive enough to cover a wide range of shades
    when we use that parameter.

    We should come up with an interpolation method that shades between black
    and white depending on a gradient and a certain percentage.
    """
    from termx.config import config
    from termx.core.exceptions import FormatError

    light_limit = light_limit or 1
    dark_limit = dark_limit or 0
    slc = slice(dark_limit, -1 * light_limit, gradient)
    shades = config.Colors.SHADES[slc]

    if len(shades) == 0:
        raise FormatError('Invalid shade limits.')

    # fmt = Format(color=shades[level], styles=styles)
    # import ipdb; ipdb.set_trace()
    try:
        return shades[level]
    except IndexError:
        return shades[-1]
