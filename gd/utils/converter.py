import re

from .enums import DemonDifficulty, LevelDifficulty, GauntletEnum

from .._typing import Union
from ..song import Song


# song-related dict
_cases = {
    -1: ('OcularNebula', 'Practice: Stay Inside Me'),
    0: ('ForeverBound', 'Stereo Madness'),
    1: ('DJVI', 'Back On Track'),
    2: ('Step', 'Polargeist'),
    3: ('DJVI', 'Dry Out'),
    4: ('DJVI', 'Base After Base'),
    5: ('DJVI', 'Cant Let Go'),
    6: ('Waterflame', 'Jumper'),
    7: ('Waterflame', 'Time Machine'),
    8: ('DJVI', 'Cycles'),
    9: ('DJVI', 'xStep'),
    10: ('Waterflame', 'Clutterfunk'),
    11: ('DJ-Nate', 'Theory of Everything'),
    12: ('Waterflame', 'Electroman Adventures'),
    13: ('DJ-Nate', 'Clubstep'),
    14: ('DJ-Nate', 'Electrodynamix'),
    15: ('Waterflame', 'Hexagon Force'),
    16: ('Waterflame', 'Blast Processing'),
    17: ('DJ-Nate', 'Theory of Everything 2'),
    18: ('Waterflame', 'Geometrical Dominator'),
    19: ('F-777', 'Deadlocked'),
    20: ('MDK', 'Fingerdash'),
    21: ('F-777', 'The Seven Seas'),
    22: ('F-777', 'Viking Arena'),
    23: ('F-777', 'Airborne Robots'),
    24: ('RobTop', 'Secret'),  # aka DJRubRub, haha
    25: ('Dex Arson', 'Payload'),
    26: ('Dex Arson', 'Beast Mode'),
    27: ('Dex Arson', 'Machina'),
    28: ('Dex Arson', 'Years'),
    29: ('Dex Arson', 'Frontline'),
    30: ('Waterflame', 'Space Pirates'),
    31: ('Waterflame', 'Striker'),
    32: ('Dex Arson', 'Embers'),
    33: ('Dex Arson', 'Round 1'),
    34: ('F-777', 'Monster Dance Off'),
}


class Converter:
    """Some weird class where NeKit holds his converters for everything"""
    @classmethod
    def to_normal_song(cls, song_id: int, server_style: bool = True) -> Song:
        if server_style:
            cases = _cases
        else:
            cases = {number + 1: value for number, value in _cases.items()}

        # get author and name, just like gd does
        author, name = cases.get(song_id, ('DJVI', 'Unknown'))
        return Song(
            name=name, author=author, id=song_id,
            size=0.0, links={}, custom=False
        )

    @classmethod
    def to_ordinal(cls, n: int) -> str:
        x = str(n)

        pn = x[-2:-1]
        sn = x[-1:]

        cases = {
            '1': 'st',
            '2': 'nd',
            '3': 'rd'
        }

        res = x + (
            cases.get(sn, 'th') if pn != '1' else 'th'
        )
        return res

    @classmethod
    def snake_to_camel(cls, string: str) -> str:  # not perfect but still...
        return re.sub('_([a-zA-Z0-9])', lambda match: match.group(1).upper(), string)

    @classmethod
    def get_gauntlet_name(cls, value: int) -> str:
        return GauntletEnum.from_value(value).desc + ' ' + 'Gauntlet'

    @classmethod
    def value_to_pack_difficulty(cls, value: int) -> LevelDifficulty:
        cases = {
            1: LevelDifficulty.EASY,
            2: LevelDifficulty.NORMAL,
            3: LevelDifficulty.HARD,
            4: LevelDifficulty.HARDER,
            5: LevelDifficulty.INSANE,
            6: LevelDifficulty.DEMON
        }
        return cases.get(value, LevelDifficulty.NA)

    @classmethod
    def value_to_difficulty(cls, value: int) -> LevelDifficulty:
        cases = {
            10: LevelDifficulty.EASY,
            20: LevelDifficulty.NORMAL,
            30: LevelDifficulty.HARD,
            40: LevelDifficulty.HARDER,
            50: LevelDifficulty.INSANE
        }
        return cases.get(value, LevelDifficulty.NA)

    @classmethod
    def value_to_demon(cls, value: int) -> DemonDifficulty:
        cases = {
            3: DemonDifficulty.EASY_DEMON,
            4: DemonDifficulty.MEDIUM_DEMON,
            5: DemonDifficulty.INSANE_DEMON,
            6: DemonDifficulty.EXTREME_DEMON
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
