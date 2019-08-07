from .enums import DemonDifficulty, LevelDifficulty

from ..song import Song

class Converter:
    """Some weird class where NeKit holds his converters for everything"""
    def to_normal_song(song_id: int):
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
            name = name, author = author, id = id,
            size = None, links = (None, None), custom = False
        )

    def to_ordinal(n: int):
        x = str(n)
        sn = int(x[-1])
        cases = {
            1: 'st',
            2: 'nd',
            3: 'rd'
        }
        res = x + cases.get(sn, 'th')
        return res

    def value_to_difficulty(value: int):
        cases = {
            10: LevelDifficulty.EASY,
            20: LevelDifficulty.NORMAL,
            30: LevelDifficulty.HARD,
            40: LevelDifficulty.HARDER,
            50: LevelDifficulty.INSANE
        }
        return cases.get(value, LevelDifficulty.NA)

    def value_to_demon(value: int):
        cases = {
            3: DemonDifficulty.EASY_DEMON,
            4: DemonDifficulty.MEDIUM_DEMON,
            5: DemonDifficulty.INSANE_DEMON,
            6: DemonDifficulty.EXTREME_DEMON
        }
        return cases.get(value, DemonDifficulty.HARD_DEMON)

    def convert_level_difficulty(diff: int, demon_diff: int, is_demon: bool, is_auto: bool):
        if is_auto:
            return LevelDifficulty.AUTO
        if is_demon:
            return value_to_demon(demon_diff)
        return value_to_difficulty(diff)