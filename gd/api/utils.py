from gd.typing import Any, Dict, Struct
from gd.errors import EditorError
from gd.colors import Color

from gd.api.enums import (
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

__all__ = ("supported", "get_id", "get_default")


def get_id(x: str, ret_enum: bool = False, delim: str = ":") -> Any:
    """Calculate required value from the given directive ``x``.

    The format is, as follows: ``class:name``, e.g. ``special:h``.
    Spaces around ``:`` are allowed.

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
        string.strip().replace("_", "").lower() for string in x.split(delim, maxsplit=1)
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
        raise EditorError(f"ID by directive {x!r} was not found.") from None


def get_default(name: str) -> Dict[Any, Any]:
    return default.get(name, {})


mapping = {
    "special": SpecialBlockType,
    "trigger": TriggerType,
    "portal": PortalType,
    "orb": OrbType,
    "pad": PadType,
    "easing": Easing,
    "layer": ZLayer,
    "color": SpecialColorID,
    "misc": MiscType,
}

supported = {name: enum.as_dict() for name, enum in mapping.items()}

# because variables can not start with digits, we are doing this
supported.get("color", {}).update({"3dl": "color:line3d"})
supported.get("portal", {}).update(
    {
        f"speed:x{index}": f"portal:{string}speed"
        for index, string in enumerate(("slow", "normal", "fast", "faster", "fastest"))
    }
)


def _make_color(struct: Struct) -> Color:
    channels = (struct.r, struct.g, struct.b)

    if None in channels:
        return Color()

    return Color.from_rgb(*channels)


def _define_color(color: Any) -> Color:
    if _iterable(color):
        return Color.from_rgb(*color)

    if isinstance(color, Color):
        return Color(color.value)

    return Color(color)


def _get_dir(directive: str, cls: str, delim: str = ":") -> str:
    return delim.join((cls, directive.split(delim).pop()))


def _iterable(maybe_iterable: Any) -> bool:
    try:
        iter(maybe_iterable)
        return True
    except Exception:  # noqa
        return False


# a large dictionary containing all default values for various objects

default = {
    "object": {"1": 1, "2": 0, "3": 0},
    "color_channel": {
        "1": 255,
        "2": 255,
        "3": 255,
        "4": -1,
        "5": False,
        "6": 0,
        "7": 1,
        "8": True,
        "11": 255,
        "12": 255,
        "13": 255,
        "15": True,
        "18": False,
    },
    "header": {
        "kA2": 0,
        "kA3": False,
        "kA4": 0,
        "kA6": 0,
        "kA7": 0,
        "kA8": False,
        "kA9": False,
        "kA10": False,
        "kA11": False,
        "kA13": 0,
        "kA14": [],
        "kA15": False,
        "kA16": False,
        "kA17": False,
        "kA18": 0,
        "kS38": [],
        "kS39": 0,
    },
    "api": {"kCEK": 4, "k2": "Unnamed", "k4": "", "k13": True, "k16": 1, "k47": True, "k50": 35},
    "main": {
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
    },
    "levels": {"LLM_01": {"_isArr": True}, "LLM_02": 35},
}
