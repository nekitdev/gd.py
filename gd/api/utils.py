import base64
import json

from .._typing import Any, Dict, Struct
from ..errors import EditorError
from ..colors import Color

from .enums import (
    SpecialBlockType,
    TriggerType,
    PortalType,
    OrbType,
    PadType,
    Easing,
    ZLayer,
    SpecialColorID,
    MiscType,
)

__all__ = ('supported', 'get_id', 'get_default')


def get_id(x: str, ret_enum: bool = False, delim: str = ':') -> Any:
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


def get_default(name: str) -> Dict[Any, Any]:
    return default.get(name, {})


def _load_default() -> Dict[Any, Any]:
    data = json.loads(base64.b64decode(_default.encode()).decode())

    final = {}

    for k, d_i in data.items():
        d = {}
        for k_i, v in d_i.items():
            try:
                k_i = int(k_i)
            except ValueError:
                pass
            finally:
                d[k_i] = v
        final[k] = d

    return final


mapping = {
    'special': SpecialBlockType,
    'trigger': TriggerType,
    'portal': PortalType,
    'orb': OrbType,
    'pad': PadType,
    'easing': Easing,
    'layer': ZLayer,
    'color': SpecialColorID,
    'misc': MiscType,
}

supported = {name: enum.as_dict() for name, enum in mapping.items()}

# because variables can not start with digits, we are doing this
supported.get('color', {}).update({'3dl': 'color:line3d'})

d = supported.get('portal', {})
for i, s in zip(range(5), ('slow', 'normal', 'fast', 'faster', 'fastest')):
    d.update({'speed:x{}'.format(i): 'portal:{}speed'.format(s)})

# do some cleanup
del i, s, d


def _make_color(struct: Struct) -> Color:
    channels = (struct.r, struct.g, struct.b)

    if None in channels:
        return Color()

    return Color.from_rgb(*channels)


def _define_color(color: Any) -> Color:
    if hasattr(color, '__iter__'):
        # something iterable
        return Color.from_rgb(*color)

    if isinstance(color, Color):
        return Color(color.value)

    return Color(color)


def _get_dir(directive: str, cls: str, delim: str = ':') -> str:
    return delim.join((cls, directive.split(delim).pop()))


# json-like dictionary, encoded in Base64
_default = """
eyJvYmplY3QiOiB7IjEiOiAxLCAiMiI6IDAsICIzIjogMH0sICJjb2xvcl9jaGFubmVsIjogeyIxIjogMjU1LCAiMiI6IDI1NSwg
IjMiOiAyNTUsICI0IjogLTEsICI1IjogZmFsc2UsICI2IjogMCwgIjciOiAxLCAiOCI6IHRydWUsICIxMSI6IDI1NSwgIjEyIjog
MjU1LCAiMTMiOiAyNTUsICIxNSI6IHRydWUsICIxOCI6IGZhbHNlfSwgImhlYWRlciI6IHsia0EyIjogMCwgImtBMyI6IGZhbHNl
LCAia0E0IjogMCwgImtBNiI6IDAsICJrQTciOiAwLCAia0E4IjogZmFsc2UsICJrQTkiOiBmYWxzZSwgImtBMTAiOiBmYWxzZSwg
ImtBMTEiOiBmYWxzZSwgImtBMTMiOiAwLCAia0ExNCI6IFtdLCAia0ExNSI6IGZhbHNlLCAia0ExNiI6IGZhbHNlLCAia0ExNyI6
IGZhbHNlLCAia0ExOCI6IDAsICJrUzM4IjogW10sICJrUzM5IjogMH0sICJhcGkiOiB7ImtDRUsiOiA0LCAiazIiOiAiVW5uYW1l
ZCIsICJrNCI6ICIiLCAiazEzIjogdHJ1ZSwgImsxNiI6IDF9LCAibWFpbiI6IHsidmFsdWVLZWVwZXIiOiB7Imd2XzAwMDEiOiAi
MSIsICJndl8wMDAyIjogIjEiLCAiZ3ZfMDAxMyI6ICIxIiwgImd2XzAwMTYiOiAiMSIsICJndl8wMDE4IjogIjEiLCAiZ3ZfMDAx
OSI6ICIxIiwgImd2XzAwMjMiOiAiMSIsICJndl8wMDI1IjogIjEiLCAiZ3ZfMDAyNiI6ICIxIiwgImd2XzAwMjciOiAiMSIsICJn
dl8wMDI5IjogIjEiLCAiZ3ZfMDAzMCI6ICIxIiwgImd2XzAwMzYiOiAiMSIsICJndl8wMDM4IjogIjEiLCAiZ3ZfMDA0MyI6ICIx
IiwgImd2XzAwNDQiOiAiMSIsICJndl8wMDQ2IjogIjEiLCAiZ3ZfMDA0OCI6ICIxIiwgImd2XzAwNDkiOiAiMSIsICJndl8wMDUw
IjogIjEiLCAiZ3ZfMDA2MyI6ICIxIiwgImd2XzAwOTgiOiAiMSJ9LCAidW5sb2NrVmFsdWVLZWVwZXIiOiB7fSwgImN1c3RvbU9i
amVjdERpY3QiOiB7fSwgImJnVm9sdW1lIjogMS4wLCAic2Z4Vm9sdW1lIjogMS4wLCAicGxheWVyVURJRCI6ICJTMTIzNDU2Nzg5
MCIsICJwbGF5ZXJOYW1lIjogIlBsYXllciIsICJwbGF5ZXJGcmFtZSI6IDEsICJwbGF5ZXJTaGlwIjogMSwgInBsYXllckJhbGwi
OiAxLCAicGxheWVyQmlyZCI6IDEsICJwbGF5ZXJEYXJ0IjogMSwgInBsYXllclJvYm90IjogMSwgInBsYXllclNwaWRlciI6IDEs
ICJwbGF5ZXJDb2xvcjIiOiAzLCAicGxheWVyU3RyZWFrIjogMSwgInBsYXllckRlYXRoRWZmZWN0IjogMSwgInJlcG9ydGVkQWNo
aWV2ZW1lbnRzIjoge30sICJHTE1fMDEiOiB7fSwgIkdMTV8wMyI6IHt9LCAiR0xNXzEwIjoge30sICJHTE1fMTYiOiB7fSwgIkdM
TV8wOSI6IHt9LCAiR0xNXzA3Ijoge30sICJHTE1fMTQiOiB7fSwgIkdMTV8xMiI6IHt9LCAiR0xNXzEzIjoge30sICJHTE1fMTUi
OiB7fSwgIkdMTV8wNiI6IHt9LCAiR0xNXzA4IjogeyJEaWZmMCI6ICIwIiwgIkRpZmYxIjogIjAiLCAiRGlmZjIiOiAiMCIsICJE
aWZmMyI6ICIwIiwgIkRpZmY0IjogIjAiLCAiRGlmZjUiOiAiMCIsICJEaWZmNiI6ICIwIiwgIkRpZmY3IjogIjAiLCAiTGVuMCI6
ICIwIiwgIkxlbjEiOiAiMCIsICJMZW4yIjogIjAiLCAiTGVuMyI6ICIwIiwgIkxlbjQiOiAiMCIsICJkZW1vbl9maWx0ZXIiOiAi
MCJ9LCAiR0xNXzE4Ijoge30sICJHTE1fMTkiOiB7fSwgIkdTX3ZhbHVlIjogeyIxIjogIjAiLCAiMiI6ICIwIiwgIjMiOiAiMCIs
ICI0IjogIjAiLCAiNSI6ICIwIiwgIjYiOiAiMCIsICI3IjogIjAiLCAiOCI6ICIwIiwgIjkiOiAiMCIsICIxMCI6ICIwIiwgIjEx
IjogIjAiLCAiMTIiOiAiMCIsICIxMyI6ICIwIiwgIjE0IjogIjAiLCAiMTUiOiAiMCIsICIxNiI6ICIwIiwgIjE3IjogIjAiLCAi
MTgiOiAiMCIsICIxOSI6ICIwIiwgIjIwIjogIjAiLCAiMjEiOiAiMCIsICIyMiI6ICIwIn0sICJHU19jb21wbGV0ZWQiOiB7fSwg
IkdTXzMiOiB7fSwgIkdTXzQiOiB7fSwgIkdTXzUiOiB7fSwgIkdTXzYiOiB7fSwgIkdTXzciOiB7fSwgIkdTXzIzIjoge30sICJH
U184Ijoge30sICJHU185Ijoge30sICJHU18xMCI6IHt9LCAiR1NfMTYiOiB7fSwgIkdTXzE3Ijoge30sICJHU18xOCI6IHt9LCAi
R1NfMjQiOiB7fSwgIkdTXzExIjoge30sICJHU18yMiI6IHt9LCAiR1NfMjUiOiB7fSwgIkdTXzEyIjoge30sICJHU18xNSI6IHt9
LCAiR1NfMTQiOiB7fSwgIkdTXzE5Ijoge30sICJHU18yMSI6IHt9LCAiTURMTV8wMDEiOiB7fSwgIktCTV8wMDEiOiB7fSwgIktC
TV8wMDIiOiB7fSwgInNob3dTb25nTWFya2VycyI6IHRydWUsICJjbGlja2VkRWRpdG9yIjogdHJ1ZSwgImNsaWNrZWRQcmFjdGlj
ZSI6IHRydWUsICJib290dXBzIjogMCwgImJpbmFyeVZlcnNpb24iOiAzNSwgInJlc29sdXRpb24iOiAtMX0sICJsZXZlbHMiOiB7
IkxMTV8wMSI6IHsiX2lzQXJyIjogdHJ1ZX0sICJMTE1fMDIiOiAzNX19
"""

default = _load_default()
