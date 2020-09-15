from gd.typing import Any, Iterable, TypeVar, Union
from gd.errors import EditorError

from gd.enums import (
    SpecialBlockType,
    TriggerType,
    PortalType,
    SpeedChange,
    OrbType,
    PadType,
    Easing,
    ZLayer,
    SpecialColorID,
    MiscType,
)

__all__ = ("get_id", "get_dir")

T = TypeVar("T")

clear_spaces_and_under = str.maketrans({"_": "", " ": ""})


def lower_name(name: str) -> str:
    return name.lower().translate(clear_spaces_and_under)


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
    type_of, delim, name = lower_name(string).partition(delim)

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
        lower_name(member_name): member.value  # type: ignore
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


def is_iterable(maybe_iterable: Union[Iterable[T], T]) -> bool:
    try:
        iter(maybe_iterable)  # type: ignore
        return True
    except TypeError:  # "T" object is not iterable
        return False


def get_dir(string: str, begin: str, delim: str = ":") -> str:
    return begin + delim + string.split(delim)[-1]


# default values for saves

MAIN_DEFAULTS = {
    "valueKeeper": {
        "gv_0001": "1",
        "gv_0002": "1",
        "gv_0013": "1",
        "gv_0016": "1",
        "gv_0018": "1",
        "gv_0019": "1",
        "gv_0023": "1",
        "gv_0025": "1",
        "gv_0026": "1",
        "gv_0027": "1",
        "gv_0029": "1",
        "gv_0030": "1",
        "gv_0036": "1",
        "gv_0038": "1",
        "gv_0043": "1",
        "gv_0044": "1",
        "gv_0046": "1",
        "gv_0048": "1",
        "gv_0049": "1",
        "gv_0050": "1",
        "gv_0063": "1",
        "gv_0098": "1",
    },
    "unlockValueKeeper": {},
    "customObjectDict": {},
    "bgVolume": 1.0,
    "sfxVolume": 1.0,
    "playerUDID": "S1234567890",
    "playerName": "Player",
    "playerFrame": 1,
    "playerShip": 1,
    "playerBall": 1,
    "playerBird": 1,
    "playerDart": 1,
    "playerRobot": 1,
    "playerSpider": 1,
    "playerColor2": 3,
    "playerStreak": 1,
    "playerDeathEffect": 1,
    "reportedAchievements": {},
    "GLM_01": {},
    "GLM_03": {},
    "GLM_10": {},
    "GLM_16": {},
    "GLM_09": {},
    "GLM_07": {},
    "GLM_14": {},
    "GLM_12": {},
    "GLM_13": {},
    "GLM_15": {},
    "GLM_06": {},
    "GLM_08": {
        "Diff0": "0",
        "Diff1": "0",
        "Diff2": "0",
        "Diff3": "0",
        "Diff4": "0",
        "Diff5": "0",
        "Diff6": "0",
        "Diff7": "0",
        "Len0": "0",
        "Len1": "0",
        "Len2": "0",
        "Len3": "0",
        "Len4": "0",
        "demon_filter": "0",
    },
    "GLM_18": {},
    "GLM_19": {},
    "GS_value": {
        "1": "0",
        "2": "0",
        "3": "0",
        "4": "0",
        "5": "0",
        "6": "0",
        "7": "0",
        "8": "0",
        "9": "0",
        "10": "0",
        "11": "0",
        "12": "0",
        "13": "0",
        "14": "0",
        "15": "0",
        "16": "0",
        "17": "0",
        "18": "0",
        "19": "0",
        "20": "0",
        "21": "0",
        "22": "0",
    },
    "GS_completed": {},
    "GS_3": {},
    "GS_4": {},
    "GS_5": {},
    "GS_6": {},
    "GS_7": {},
    "GS_23": {},
    "GS_8": {},
    "GS_9": {},
    "GS_10": {},
    "GS_16": {},
    "GS_17": {},
    "GS_18": {},
    "GS_24": {},
    "GS_11": {},
    "GS_22": {},
    "GS_25": {},
    "GS_12": {},
    "GS_15": {},
    "GS_14": {},
    "GS_19": {},
    "GS_21": {},
    "MDLM_001": {},
    "KBM_001": {},
    "KBM_002": {},
    "showSongMarkers": True,
    "clickedEditor": True,
    "clickedPractice": True,
    "bootups": 0,
    "binaryVersion": 35,
    "resolution": -1,
}

LEVELS_DEFAULTS = {
    "LLM_01": {"_isArr": True},
    "LLM_02": 35,
}
