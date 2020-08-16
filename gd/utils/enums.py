import enums

from gd.typing import Dict, Any

__all__ = (
    "Enum",
    "IconType",
    "MessagePolicyType",
    "CommentPolicyType",
    "FriendRequestPolicyType",
    "StatusLevel",
    "LevelLength",
    "LevelDifficulty",
    "DemonDifficulty",
    "TimelyType",
    "CommentType",
    "MessageOrRequestType",
    "CommentStrategy",
    "LeaderboardStrategy",
    "LevelLeaderboardStrategy",
    "SearchStrategy",
    "GauntletEnum",
    "RewardType",
    "ShardType",
    "QuestType",
    "AccountError",
)


class Enum(enums.StrFormat, enums.Order, enums.Enum):
    """Normalized generic enum that has ordering and string formatting."""

    def __json__(self) -> Dict[str, Any]:
        return {"name": self.title, "value": self.value}


class IconType(Enum):
    """An enumeration of icon types."""

    CUBE = 0
    SHIP = 1
    BALL = 2
    UFO = 3
    WAVE = 4
    ROBOT = 5
    SPIDER = 6


class MessagePolicyType(Enum):
    """An enumeration for message policy."""

    OPENED_TO_ALL = 0
    OPENED_TO_FRIENDS_ONLY = 1
    CLOSED = 2


class CommentPolicyType(Enum):
    """An enumeration for comment policy."""

    OPENED_TO_ALL = 0
    OPENED_TO_FRIENDS_ONLY = 1
    CLOSED = 2


class FriendRequestPolicyType(Enum):
    """An enumeration for friend request policy."""

    OPENED = 0
    CLOSED = 1


class StatusLevel(Enum):
    """An enumeration for Geometry Dash Status."""

    USER = 0
    MODERATOR = 1
    ELDER_MODERATOR = 2


class LevelLength(Enum):
    """An enumeration for level lengths."""

    NA = -1
    TINY = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    EXTRA_LONG = 4
    XL = EXTRA_LONG

    UNKNOWN = NA

    @classmethod
    def enum_missing(cls, value: int) -> Enum:
        if value > cls.XL.value:
            return cls.XL

        if value < cls.TINY.value:
            return cls.TINY


class LevelDifficulty(Enum):
    """An enumeration for level difficulties."""

    NA = -1
    AUTO = -3
    EASY = 1
    NORMAL = 2
    HARD = 3
    HARDER = 4
    INSANE = 5
    DEMON = -2

    UNKNOWN = NA


class DemonDifficulty(Enum):
    """An enumeration for demon difficulties."""

    NA = -1
    EASY_DEMON = 1
    MEDIUM_DEMON = 2
    HARD_DEMON = 3
    INSANE_DEMON = 4
    EXTREME_DEMON = 5

    UNKNOWN = NA


class TimelyType(Enum):
    """An enumeration for timely types."""

    NOT_TIMELY = 0
    DAILY = 1
    WEEKLY = 2


class CommentType(Enum):
    """An enumeration for comment objects."""

    LEVEL = 0
    PROFILE = 1


class MessageOrRequestType(Enum):
    """An enumeration for message and friend request objects."""

    NORMAL = 0
    SENT = 1


class CommentStrategy(Enum):
    """An enumeration for comment searching."""

    RECENT = 0
    MOST_LIKED = 1


class LeaderboardStrategy(Enum):
    """An enumeration for getting leaderboard users."""

    PLAYERS = 0
    FRIENDS = 1
    RELATIVE = 2
    CREATORS = 3


class LevelLeaderboardStrategy(Enum):
    """An enumeration for getting level leaderboard."""

    FRIENDS = 0
    ALL = 1
    WEEKLY = 2


class GauntletEnum(Enum):
    """An enumeration for gauntlets."""

    UNKNOWN = 0
    FIRE = 1
    ICE = 2
    POISON = 3
    SHADOW = 4
    LAVA = 5
    BONUS = 6
    CHAOS = 7
    DEMON = 8
    TIME = 9
    CRYSTAL = 10
    MAGIC = 11
    SPIKE = 12
    MONSTER = 13
    DOOM = 14
    DEATH = 15


class SearchStrategy(Enum):
    """An enumeration for search strategy."""

    REGULAR = 0
    MOST_DOWNLOADED = 1
    MOST_LIKED = 2
    TRENDING = 3
    RECENT = 4
    BY_USER = 5
    FEATURED = 6
    MAGIC = 7
    SEARCH_MANY = 10
    AWARDED = 11
    FOLLOWED = 12
    FRIENDS = 13
    HALL_OF_FAME = 16
    WORLD = 17


class RewardType(Enum):
    """An enumeration for reward types."""

    GET_INFO = 0
    CLAIM_SMALL = 1
    CLAIM_LARGE = 2


class ShardType(Enum):
    """An enumeration represeting shard names."""

    UNKNOWN = 0
    FIRE = 1
    ICE = 2
    POISON = 3
    SHADOW = 4
    LAVA = 5
    NULL = 6


class QuestType(Enum):
    """An enumeration for quest types."""

    UNKNOWN = 0
    ORBS = 1
    COINS = 2
    STARS = 3


class AccountError(Enum):
    """An enumeration for account errors."""

    EMAILS_NOT_MATCHING = -99
    LINKED_TO_DIFFERENT_STEAM_ACCOUNT = -12
    ACCOUNT_DISABLED = -11
    LINKED_TO_DIFFERENT_ACCOUNT = -10
    SHORT_USERNAME = -9
    SHORT_PASSWORD = -8
    PASSWORDS_NOT_MATCHING = -7
    INVALID_EMAIL = -6
    INVALID_PASSWORD = -5
    INVALID_USERNAME = -4
    EMAIL_USED = -3
    USERNAME_USED = -2
    GENERIC = -1
