import re

from gd.utils.enums import DemonDifficulty, LevelDifficulty, GauntletEnum
from gd.utils.parser import ExtDict

from gd.typing import Union


# song-related dict
_cases = {
    -1: ("OcularNebula", "Practice: Stay Inside Me"),
    0: ("ForeverBound", "Stereo Madness"),
    1: ("DJVI", "Back On Track"),
    2: ("Step", "Polargeist"),
    3: ("DJVI", "Dry Out"),
    4: ("DJVI", "Base After Base"),
    5: ("DJVI", "Cant Let Go"),
    6: ("Waterflame", "Jumper"),
    7: ("Waterflame", "Time Machine"),
    8: ("DJVI", "Cycles"),
    9: ("DJVI", "xStep"),
    10: ("Waterflame", "Clutterfunk"),
    11: ("DJ-Nate", "Theory of Everything"),
    12: ("Waterflame", "Electroman Adventures"),
    13: ("DJ-Nate", "Clubstep"),
    14: ("DJ-Nate", "Electrodynamix"),
    15: ("Waterflame", "Hexagon Force"),
    16: ("Waterflame", "Blast Processing"),
    17: ("DJ-Nate", "Theory of Everything 2"),
    18: ("Waterflame", "Geometrical Dominator"),
    19: ("F-777", "Deadlocked"),
    20: ("MDK", "Fingerdash"),
    21: ("F-777", "The Seven Seas"),
    22: ("F-777", "Viking Arena"),
    23: ("F-777", "Airborne Robots"),
    24: ("RobTop", "Secret"),  # aka DJRubRub, haha
    25: ("Dex Arson", "Payload"),
    26: ("Dex Arson", "Beast Mode"),
    27: ("Dex Arson", "Machina"),
    28: ("Dex Arson", "Years"),
    29: ("Dex Arson", "Frontlines"),
    30: ("Waterflame", "Space Pirates"),
    31: ("Waterflame", "Striker"),
    32: ("Dex Arson", "Embers"),
    33: ("Dex Arson", "Round 1"),
    34: ("F-777", "Monster Dance Off"),
    35: ("MDK", "Press Start"),
    36: ("Bossfight", "Nock Em"),
    37: ("Boom Kitty", "Power Trip"),
}


class Converter:
    """Some weird class where nekit holds his converters for everything."""

    @staticmethod
    def to_normal_song(song_id: int, server_style: bool = True) -> ExtDict:
        if server_style:
            cases = _cases
        else:
            cases = {number + 1: value for number, value in _cases.items()}

        # get author and name, just like gd does
        author, name = cases.get(song_id, ("DJVI", "Unknown"))
        return ExtDict(name=name, author=author, id=song_id, size=0.0, links={}, custom=False)

    @staticmethod
    def to_ordinal(n: int) -> str:
        cases = {1: "st", 2: "nd", 3: "rd"}
        x = abs(n)

        if 11 <= x % 100 <= 13:
            return str(n) + "th"

        else:
            return str(n) + cases.get(x % 10, "th")

    @staticmethod
    def snake_to_camel(string: str) -> str:  # not perfect but still...
        return re.sub("_([a-zA-Z0-9])", lambda match: match.group(1).upper(), string)

    @staticmethod
    def get_gauntlet_name(value: int) -> str:
        gauntlet = GauntletEnum.from_value(value, 0).title
        return f"{gauntlet} Gauntlet"

    @staticmethod
    def get_gauntlet_id(name: str) -> int:
        check = "Gauntlet"

        if name.endswith(check):
            name = name[: -len(check)]

        name = name.strip()

        gauntlet = GauntletEnum.from_value(name, "unknown").value

        return gauntlet

    @staticmethod
    def value_to_pack_difficulty(value: int) -> LevelDifficulty:
        cases = {
            1: LevelDifficulty.EASY,
            2: LevelDifficulty.NORMAL,
            3: LevelDifficulty.HARD,
            4: LevelDifficulty.HARDER,
            5: LevelDifficulty.INSANE,
            6: LevelDifficulty.DEMON,
        }
        return cases.get(value, LevelDifficulty.NA)

    @staticmethod
    def value_to_difficulty(value: int) -> LevelDifficulty:
        cases = {
            10: LevelDifficulty.EASY,
            20: LevelDifficulty.NORMAL,
            30: LevelDifficulty.HARD,
            40: LevelDifficulty.HARDER,
            50: LevelDifficulty.INSANE,
        }
        return cases.get(value, LevelDifficulty.NA)

    @staticmethod
    def value_to_demon(value: int) -> DemonDifficulty:
        cases = {
            3: DemonDifficulty.EASY_DEMON,
            4: DemonDifficulty.MEDIUM_DEMON,
            5: DemonDifficulty.INSANE_DEMON,
            6: DemonDifficulty.EXTREME_DEMON,
        }
        return cases.get(value, DemonDifficulty.HARD_DEMON)

    @classmethod
    def convert_level_difficulty(
        cls, diff: int, demon_diff: int, is_demon: bool, is_auto: bool
    ) -> Union[LevelDifficulty, DemonDifficulty]:
        if is_auto:
            return LevelDifficulty.AUTO
        if is_demon:
            return cls.value_to_demon(demon_diff)
        return cls.value_to_difficulty(diff)
