import re

from .enums import DemonDifficulty, LevelDifficulty

from ..song import Song

class Converter:
    """Some weird class where NeKit holds his converters for everything"""
    @classmethod
    def to_normal_song(cls, song_id: int):
        cases = {
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
        }
        author, name = cases.get(song_id, (None, None))
        return Song(
            name = name, author = author, id = song_id,
            size = None, links = {}, custom = False
        )

    @classmethod
    def to_ordinal(cls, n: int):
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
    def snake_to_camel(cls, string: str):  # not perfect but still...
        return re.sub('_([a-zA-Z0-9])', lambda match: match.group(1).upper(), string)

    @classmethod
    def value_to_pack_difficulty(cls, value: int):
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
    def value_to_difficulty(cls, value: int):
        cases = {
            10: LevelDifficulty.EASY,
            20: LevelDifficulty.NORMAL,
            30: LevelDifficulty.HARD,
            40: LevelDifficulty.HARDER,
            50: LevelDifficulty.INSANE
        }
        return cases.get(value, LevelDifficulty.NA)

    @classmethod
    def value_to_demon(cls, value: int):
        cases = {
            3: DemonDifficulty.EASY_DEMON,
            4: DemonDifficulty.MEDIUM_DEMON,
            5: DemonDifficulty.INSANE_DEMON,
            6: DemonDifficulty.EXTREME_DEMON
        }
        return cases.get(value, DemonDifficulty.HARD_DEMON)

    @classmethod
    def convert_level_difficulty(cls, diff: int, demon_diff: int, is_demon: bool, is_auto: bool):
        if is_auto:
            return LevelDifficulty.AUTO
        if is_demon:
            return cls.value_to_demon(demon_diff)
        return cls.value_to_difficulty(diff)
