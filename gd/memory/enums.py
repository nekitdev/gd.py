from gd.utils.enums import Enum

__all__ = ("GameMode", "LevelType", "Scene")


class Scene(Enum):
    """An enumeration that represents ID of different scenes in the game."""

    UNKNOWN = -1
    MAIN = 0
    SELECT = 1
    OLD_MY_LEVELS = 2
    EDITOR_OR_LEVEL = 3
    SEARCH = 4
    UNUSED = 5
    LEADERBOARD = 6
    ONLINE = 7
    OFFICIAL_LEVELS = 8
    OFFICIAL_LEVEL = 9
    THE_CHALLENGE = 12


class LevelType(Enum):
    """An enumeration that represents type of the level that is being played."""

    NULL = 0
    OFFICIAL = 1
    EDITOR = 2
    SAVED = 3
    ONLINE = 4


class GameMode(Enum):
    """An enumeration that represents gamemodes."""

    CUBE = 0
    SHIP = 1
    BALL = 2
    UFO = 3
    WAVE = 4
    ROBOT = 5
    SPIDER = 6
