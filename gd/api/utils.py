from gd.enums import (
    Easing,
    MiscType,
    OrbType,
    PadType,
    PortalType,
    SpecialBlockType,
    SpecialColorID,
    SpeedChange,
    TriggerType,
    ZLayer,
)
from gd.errors import EditorError
from gd.typing import Any

__all__ = ("get_id", "get_dir")

clear_space_and_underscore = str.maketrans({"_": "", " ": ""})


def casefold_string(string: str) -> str:
    return string.casefold().translate(clear_space_and_underscore)


def get_id(string: str, into_enum: bool = False, delim: str = ":") -> Any:
    """Calculate required value from the given directive ``string``.

    The format is, as follows: ``class:name``, e.g. ``special:h``.
    Spaces around ``:`` are allowed.

    Parameters
    ----------
    string: :class:`str`
        Directive to get value from.

    into_enum: :class:`bool`
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
    type_of, delim, name = casefold_string(string).partition(delim)

    if not delim:
        raise ValueError(f"Invalid directive was provided: {string!r}")

    try:
        found = supported[type_of][name]

        if isinstance(found, str) and delim in found:
            return get_id(found, into_enum=into_enum, delim=delim)

        if into_enum:
            return dir_enums[type_of](found)

        return found

    except KeyError:
        raise EditorError(f"ID by directive {string!r} was not found.") from None


dir_enums = {
    "special": SpecialBlockType,
    "trigger": TriggerType,
    "portal": PortalType,
    "orb": OrbType,
    "pad": PadType,
    "easing": Easing,
    "layer": ZLayer,
    "color": SpecialColorID,
    "misc": MiscType,
    "speed": SpeedChange,
}

supported = {
    name: {
        casefold_string(member_name): member.value  # type: ignore
        for member_name, member in enum.members.items()  # type: ignore
    }
    for name, enum in dir_enums.items()
}

speeds = {
    0.5: SpeedChange.SLOW,
    1: SpeedChange.NORMAL,
    2: SpeedChange.FAST,
    3: SpeedChange.FASTER,
    4: SpeedChange.FASTEST,
}

# because variables can not start with digits, we are doing this
supported.get("color", {}).update({"3dl": "color:line3d"})
supported.get("speed", {}).update(
    {
        f"x{mental_mul}": f"speed:{speed.name.lower()}"  # type: ignore
        for mental_mul, speed in speeds.items()
    }
)


def get_dir(string: str, begin: str, delim: str = ":") -> str:
    return begin + delim + string.split(delim)[-1]
