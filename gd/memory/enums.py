from gd.utils.enums import Enum

__all__ = ("Scene",)


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
