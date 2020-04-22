from ..typing import Any
from ..utils.enums import NEnum as Enum

__all__ = ("Scene",)


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
    MAIN_LEVELS = 8
    MAIN_LEVEL = 9
    THE_CHALLENGE = 12

    @classmethod
    def from_value(cls, value: Any) -> Enum:
        try:
            return super().from_value(value)
        except Exception:
            return cls.UNKNOWN
