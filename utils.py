from .constants import COLOR_MAP
from .compat import ( # noqa
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


def get_color(value):
    """
    [x] TODO:
    --------
    Replace with more consistent color formatting scheme, one consistent
    with artsylogger or change artsylogger to use more consistent color
    scheme.
    """
    available_values = [k for k, v in iteritems(COLOR_MAP) if v == "color"]
    if value not in available_values:
        raise ValueError(f"{value} Unsupportd Color Value")
    return value
