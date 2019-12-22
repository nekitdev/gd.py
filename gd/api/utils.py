from ..errors import EditorError
from ..colors import Color

from .enums import *
from .hsv import HSV

__all__ = ('supported', 'get_id')


def get_id(x: str, ret_enum: bool = False, delim: str = ':'):
    """Calculate required value from the given directive ``x``.

    The format is, as follows: ``class:name``, e.g. ``special:h``.

    Parameters
    ----------
    x: :class:`str`
        Directive to get value from.

    ret_enum: :class:`bool`
        Whether to convert found value to enum. By default, ``False``.

    delim: :class:`str`
        Character to split given directive string with.
        It is not recommended to pass this argument to the function.

    Returns
    -------
    `Any`
        The value found, if any.

    Raises
    ------
    :exc:`.EditorError`
        Failed to convert directive to the value.
    """
    typeof, name = (
        string.strip().replace('_', '').lower()
        for string in x.split(delim, maxsplit=1)
    )

    try:
        found = supported[typeof][name]

        if isinstance(found, str) and delim in found:
            # inner directive
            return get_id(found)

        elif ret_enum:
            return mapping[typeof](found)

        return found

    except Exception:
        raise EditorError('ID by directive {!r} was not found.'.format(x)) from None


mapping = {
    'special': SpecialBlockType,
    'trigger': TriggerType,
    'portal': PortalType,
    'orb': OrbType,
    'pad': PadType,
    'easing': Easing,
    'layer': ZLayer,
    'color': SpecialColorID,
}

supported = {name: enum.as_dict() for name, enum in mapping.items()}

# because variables can not start with digits, we are doing this
supported.get('color', {}).update({'3dl': 'color:line3d'})

d = supported.get('portal', {})
for i, s in zip(range(5), ('slow', 'normal', 'fast', 'faster', 'fastest')):
    d.update({'speed:x{}'.format(i): 'portal:{}speed'.format(s)})

# do some cleanup
del i, s, d


def _define_color(color):
    if hasattr(color, '__iter__'):
        # something iterable
        return Color.from_rgb(*color)

    if isinstance(color, Color):
        return Color(color.value)

    return Color(color)


def _get_dir(directive: str, cls: str, delim: str = ':'):
    return delim.join((cls, directive.split(delim).pop()))
