from ..utils.enums import Enum

__all__ = ("LevelType", "Scene")


class Scene(Enum):
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
    NULL = 0
    OFFICIAL = 1
    EDITOR = 2
    SAVED = 3
    ONLINE = 4
