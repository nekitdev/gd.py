from __future__ import annotations

from typing import Optional, Type, TypeVar

from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS, EMPTY
from gd.enum_extensions import Enum, Flag

__all__ = (
    "SimpleKey",
    "Key",
    "Salt",
    "Secret",
    "AccountURLType",
    "IconType",
    "MessageState",
    "CommentState",
    "FriendState",
    "FriendRequestState",
    "Role",
    "LevelLength",
    "UnlistedType",
    "LevelDifficulty",
    "Difficulty",
    "DemonDifficulty",
    "TimelyType",
    "TimelyID",
    "CommentType",
    "RelationshipType",
    "SimpleRelationshipType",
    "FriendRequestType",
    "MessageType",
    "CommentStrategy",
    "LeaderboardStrategy",
    "LevelLeaderboardStrategy",
    "LikeType",
    "GauntletID",
    "SearchStrategy",
    "RewardType",
    "ShardType",
    "QuestType",
    "Scene",
    "PlayerColor",
    "CustomParticleGrouping",
    "CustomParticleProperty",
    "Easing",
    "EasingMethod",
    "PulseMode",
    "InstantCountComparison",
    "OrbType",
    "PadType",
    "PickupItemMode",
    "GameMode",
    "LevelType",
    "PortalType",
    "SpeedChange",
    "PulseTargetType",
    "PulseType",
    "SpecialBlockType",
    "SpecialColorID",
    "TargetType",
    "TouchToggleMode",
    "MiscType",
    "TriggerType",
    "ZLayer",
    "Speed",
    "SpeedConstant",
    "SpeedMagic",
    "GuidelineColor",
    "InternalType",
    "Filter",
    "Permissions",
    "ByteOrder",
    "Platform",
    "Orientation",
    "ResponseType",
)


class SimpleKey(Enum, unknown=True):
    SAVE = 11


class Key(Enum, unknown=True):
    """An enumeration for keys used in *XOR* ciphering."""

    MESSAGE = 14251
    QUESTS = 19847
    LEVEL_PASSWORD = 26364
    COMMENT = 29481
    USER_PASSWORD = 37526
    LEVEL_LEADERBOARD = 39673
    LEVEL = 41274
    LIKE_RATE = 58281
    CHESTS = 59182
    USER_LEADERBOARD = 85271

    def __init__(
        self, value: int, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
    ) -> None:
        self.string = string = str(value)
        self.bytes = string.encode(encoding, errors)


class Salt(Enum, unknown=True):
    """An enumeration for salts used in hashing."""

    LEVEL = "xI25fpAapCQg"
    COMMENT = "xPT6iUrtws0J"
    LIKE_RATE = "ysg6pUrtjn0J"
    USER_LEADERBOARD = "xI35fsAapCRg"
    LEVEL_LEADERBOARD = "yPg6pUrtWn0J"
    QUESTS = "oC36fpYaPtdg"
    CHESTS = "pC26fpYaQCtg"

    EMPTY = EMPTY

    def __init__(
        self, string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
    ) -> None:
        self.string = string
        self.bytes = string.encode(encoding, errors)


class Secret(Enum):
    """An enumeration for request secrets."""

    MAIN = "Wmfd2893gb7"
    LEVEL = "Wmfv2898gc9"
    USER = "Wmfv3899gc9"
    MOD = "Wmfp3879gc3"


class AccountURLType(Enum):
    """An enumeration for account URL types."""

    SAVE = 1
    LOAD = 2


class IconType(Enum):
    """An enumeration of icon types."""

    CUBE = 0
    SHIP = 1
    BALL = 2
    UFO = 3
    WAVE = 4
    ROBOT = 5
    SPIDER = 6
    # SWING_COPTER = 7

    DEFAULT = CUBE


class MessageState(Enum):
    """An enumeration for message states."""

    OPEN_TO_ALL = 0
    OPEN_TO_FRIENDS = 1
    CLOSED = 2

    DEFAULT = OPEN_TO_ALL


class CommentState(Enum):
    """An enumeration for comment states."""

    OPEN_TO_ALL = 0
    OPEN_TO_FRIENDS = 1
    CLOSED = 2

    DEFAULT = OPEN_TO_ALL


class FriendState(Enum):
    """An enumeration for friend states."""

    NOT_FRIEND = 0
    FRIEND = 1
    BLOCKED = 2
    OUTGOING_REQUEST = 3
    INCOMING_REQUEST = 4

    DEFAULT = NOT_FRIEND


class FriendRequestState(Enum):
    """An enumeration for friend request states."""

    OPEN = 0
    CLOSED = 1

    DEFAULT = OPEN


class Role(Enum):
    """An enumeration for server roles."""

    USER = 0
    MODERATOR = 1
    ELDER_MODERATOR = 2

    DEFAULT = USER


class LevelLength(Enum):
    """An enumeration for level lengths."""

    TINY = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    XL = 4
    # PLATFORMER = 5

    DEFAULT = TINY


class UnlistedType(Flag):
    LISTED = 0
    UNLISTED = 1
    LISTED_TO_FRIENDS = 2

    FRIENDS_ONLY = UNLISTED | LISTED_TO_FRIENDS

    DEFAULT = LISTED

    def is_unlisted(self) -> bool:
        return type(self).UNLISTED in self

    def is_listed_to_friends(self) -> bool:
        return type(self).LISTED_TO_FRIENDS in self

    def is_friends_only(self) -> bool:
        return self.is_unlisted() and self.is_listed_to_friends()


class Difficulty(Enum):
    UNKNOWN = 0

    AUTO = 1
    EASY = 2
    NORMAL = 3
    HARD = 4
    HARDER = 5
    INSANE = 6
    DEMON = 7
    EASY_DEMON = 8
    MEDIUM_DEMON = 9
    HARD_DEMON = 10
    INSANE_DEMON = 11
    EXTREME_DEMON = 12

    NA = UNKNOWN

    DEFAULT = UNKNOWN

    def into_level_difficulty(self) -> LevelDifficulty:
        return DIFFICULTY_TO_LEVEL_DIFFICULTY[self]


class LevelDifficulty(Enum):
    """An enumeration for level difficulties."""

    UNKNOWN = -1
    DEMON = -2
    AUTO = -3
    EASY = 1
    NORMAL = 2
    HARD = 3
    HARDER = 4
    INSANE = 5
    EASY_DEMON = 6
    MEDIUM_DEMON = 7
    HARD_DEMON = 8
    INSANE_DEMON = 9
    EXTREME_DEMON = 10

    NA = UNKNOWN

    DEFAULT = UNKNOWN

    def into_difficulty(self) -> Difficulty:
        return LEVEL_DIFFICULTY_TO_DIFFICULTY[self]


LEVEL_DIFFICULTY_TO_DIFFICULTY = {
    LevelDifficulty.UNKNOWN: Difficulty.UNKNOWN,
    LevelDifficulty.AUTO: Difficulty.AUTO,
    LevelDifficulty.EASY: Difficulty.EASY,
    LevelDifficulty.NORMAL: Difficulty.NORMAL,
    LevelDifficulty.HARD: Difficulty.HARD,
    LevelDifficulty.HARDER: Difficulty.HARDER,
    LevelDifficulty.INSANE: Difficulty.INSANE,
    LevelDifficulty.DEMON: Difficulty.DEMON,
    LevelDifficulty.EASY_DEMON: Difficulty.EASY_DEMON,
    LevelDifficulty.MEDIUM_DEMON: Difficulty.MEDIUM_DEMON,
    LevelDifficulty.HARD_DEMON: Difficulty.HARD_DEMON,
    LevelDifficulty.INSANE_DEMON: Difficulty.INSANE_DEMON,
    LevelDifficulty.EXTREME_DEMON: Difficulty.EXTREME_DEMON,
}


DIFFICULTY_TO_LEVEL_DIFFICULTY = {
    difficulty: level_difficulty
    for level_difficulty, difficulty in LEVEL_DIFFICULTY_TO_DIFFICULTY.items()
}


class DemonDifficulty(Enum):
    """An enumeration for demon difficulties."""

    UNKNOWN = -1

    DEMON = 0
    EASY_DEMON = 1
    MEDIUM_DEMON = 2
    HARD_DEMON = 3
    INSANE_DEMON = 4
    EXTREME_DEMON = 5

    NA = UNKNOWN

    DEFAULT = UNKNOWN

    def into_difficulty(self) -> Difficulty:
        return DEMON_DIFFICULTY_TO_DIFFICULTY[self]


DEMON_DIFFICULTY_TO_DIFFICULTY = {
    DemonDifficulty.UNKNOWN: Difficulty.UNKNOWN,
    DemonDifficulty.DEMON: Difficulty.DEMON,
    DemonDifficulty.EASY_DEMON: Difficulty.EASY_DEMON,
    DemonDifficulty.MEDIUM_DEMON: Difficulty.MEDIUM_DEMON,
    DemonDifficulty.HARD_DEMON: Difficulty.HARD_DEMON,
    DemonDifficulty.INSANE_DEMON: Difficulty.INSANE_DEMON,
    DemonDifficulty.EXTREME_DEMON: Difficulty.EXTREME_DEMON,
}


class TimelyType(Enum):
    """An enumeration for timely types."""

    NOT_TIMELY = 0
    DAILY = 1
    WEEKLY = 2
    # EVENT = 3

    DEFAULT = NOT_TIMELY

    def into_timely_id(self) -> TimelyID:
        return TIMELY_TYPE_TO_ID[self]

    def is_not_timely(self) -> bool:
        return self is type(self).NOT_TIMELY

    def is_daily(self) -> bool:
        return self is type(self).DAILY

    def is_weekly(self) -> bool:
        return self is type(self).WEEKLY


class TimelyID(Enum):
    """An enumeration for timely level IDs."""

    NOT_TIMELY = 0
    DAILY = -1
    WEEKLY = -2
    # EVENT = -3

    DEFAULT = NOT_TIMELY

    def into_timely_type(self) -> TimelyType:
        return TIMELY_ID_TO_TYPE[self]

    def is_not_timely(self) -> bool:
        return self is type(self).NOT_TIMELY

    def is_daily(self) -> bool:
        return self is type(self).DAILY

    def is_weekly(self) -> bool:
        return self is type(self).WEEKLY


TIMELY_TYPE_TO_ID = {
    TimelyType.NOT_TIMELY: TimelyID.NOT_TIMELY,
    TimelyType.DAILY: TimelyID.DAILY,
    TimelyType.WEEKLY: TimelyID.WEEKLY,
    # TimelyType.EVENT: TimelyID.EVENT,
}

TIMELY_ID_TO_TYPE = {timely_id: timely_type for timely_type, timely_id in TIMELY_TYPE_TO_ID.items()}


S = TypeVar("S", bound="Score")


class Score(Enum):
    EPIC_ONLY = -2
    UNFEATURED = -1
    NOT_FEATURED = 0
    FEATURED = 1

    @classmethod
    def enum_missing(cls: Type[S], value: int) -> Optional[S]:
        return cls.FEATURED if value > 0 else None

    def is_epic_only(self) -> bool:
        return self is type(self).EPIC_ONLY

    def is_unfeatured(self) -> bool:
        return self is type(self).UNFEATURED

    def is_featured(self) -> bool:
        return self is type(self).FEATURED


class CommentType(Enum):
    """An enumeration for comment objects."""

    LEVEL = 0
    USER = 1


class RelationshipType(Enum):
    FRIEND = 1
    BLOCKED = 2
    INCOMING_REQUEST = 3
    OUTGOING_REQUEST = 4


class SimpleRelationshipType(Enum):
    FRIEND = 0
    BLOCKED = 1

    def is_friend(self) -> bool:
        return self is self.FRIEND

    def is_outgoing(self) -> bool:
        return self is self.BLOCKED

    def into_relationship_type(self) -> RelationshipType:
        return RelationshipType.FRIEND if self.is_friend() else RelationshipType.BLOCKED


class FriendRequestType(Enum):
    """An enumeration for friend request objects."""

    INCOMING = 0
    OUTGOING = 1

    DEFAULT = INCOMING

    def is_incoming(self) -> bool:
        return self is self.INCOMING

    def is_outgoing(self) -> bool:
        return self is self.OUTGOING

    def into_relationship_type(self) -> RelationshipType:
        return (
            RelationshipType.INCOMING_REQUEST
            if self.is_incoming()
            else RelationshipType.OUTGOING_REQUEST
        )


class MessageType(Enum):
    """An enumeration for message objects."""

    INCOMING = 0
    OUTGOING = 1

    DEFAULT = INCOMING

    def is_incoming(self) -> bool:
        return self is self.INCOMING

    def is_outgoing(self) -> bool:
        return self is self.OUTGOING


class CommentStrategy(Enum):
    """An enumeration for comment searching."""

    RECENT = 0
    MOST_LIKED = 1

    DEFAULT = RECENT


class LeaderboardStrategy(Enum):
    """An enumeration for getting leaderboard users."""

    TOP = 0
    PLAYERS = 0
    FRIENDS = 1
    RELATIVE = 2
    CREATORS = 3

    DEFAULT = PLAYERS

    def requires_login(self) -> bool:
        return self in REQUIRES_LOGIN


REQUIRES_LOGIN = {LeaderboardStrategy.FRIENDS, LeaderboardStrategy.RELATIVE}


class LevelLeaderboardStrategy(Enum):
    """An enumeration for getting level leaderboard."""

    FRIENDS = 0
    ALL = 1
    WEEKLY = 2

    DEFAULT = ALL


class LikeType(Enum):
    """An enumeration for sending ratings for entities."""

    LEVEL = 1
    LEVEL_COMMENT = 2
    USER_COMMENT = 3


class GauntletID(Enum):
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

    DEFAULT = 0
    MOST_DOWNLOADED = 1
    MOST_LIKED = 2
    TRENDING = 3
    RECENT = 4
    BY_USER = 5
    FEATURED = 6
    MAGIC = 7
    SENT = 8
    SEARCH_MANY = 10
    AWARDED = 11
    FOLLOWED = 12
    FRIENDS = 13
    MOST_LIKED_WORLD = 15
    HALL_OF_FAME = 16
    FEATURED_WORLD = 17
    UNKNOWN = 18
    DAILY_HISTORY = 21
    WEEKLY_HISTORY = 22


class RewardType(Enum):
    """An enumeration for reward types."""

    GET_INFO = 0
    CLAIM_SMALL = 1
    CLAIM_LARGE = 2

    DEFAULT = GET_INFO


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


class Scene(Enum):
    """An enumeration that represents IDs of different scenes in the game."""

    UNKNOWN = -1
    MAIN = 0
    SELECT = 1
    OLD = 2
    EDITOR_OR_LEVEL = 3
    SEARCH = 4
    UNUSED = 5
    LEADERBOARD = 6
    ONLINE = 7
    OFFICIAL_SELECT = 8
    OFFICIAL_LEVEL = 9
    THE_CHALLENGE = 12


class PlayerColor(Enum):
    """An enumeration for player color setting."""

    NOT_USED = -1
    DEFAULT = 0
    COLOR_1 = 1
    COLOR_2 = 2

    P1 = COLOR_1
    P2 = COLOR_2

    def is_not_used(self) -> bool:
        return self is type(self).NOT_USED

    def is_default(self) -> bool:
        return self is type(self).DEFAULT


class CustomParticleGrouping(Enum):
    """An enumeration for particle grouping."""

    FREE = 0
    RELATIVE = 1
    GROUPED = 2


class CustomParticleProperty(Enum):
    """An enumeration for particle system."""

    GRAVITY = 0
    RADIUS = 1


class Easing(Enum):
    """An enumeration representing easing of a moving object (used in move and rotate triggers)."""

    NONE = 0
    EASE_IN_OUT = 1
    EASE_IN = 2
    EASE_OUT = 3
    ELASTIC_IN_OUT = 4
    ELASTIC_IN = 5
    ELASTIC_OUT = 6
    BOUNCE_IN_OUT = 7
    BOUNCE_IN = 8
    BOUNCE_OUT = 9
    EXPONENTIAL_IN_OUT = 10
    EXPONENTIAL_IN = 11
    EXPONENTIAL_OUT = 12
    SINE_IN_OUT = 13
    SINE_IN = 14
    SINE_OUT = 15
    BACK_IN_OUT = 16
    BACK_IN = 17
    BACK_OUT = 18

    DEFAULT = NONE


EM = TypeVar("EM", bound="EasingMethod")


class EasingMethod(Flag):
    NONE = 0
    IN = 1
    OUT = 2
    EASE = 4
    ELASTIC = 8
    BOUNCE = 16
    EXPONENTIAL = 32
    SINE = 64
    BACK = 128

    DEFAULT = NONE

    def into_easing(self) -> Easing:
        cls = type(self)
        value = self.value

        if not value:
            return Easing.NONE  # type: ignore

        has_easing_in = cls.IN in self
        has_easing_out = cls.OUT in self

        if not has_easing_in and not has_easing_out:
            raise ValueError(f"{self!r} does not have In / Out modifiers.")

        value = (value.bit_length() - 2) * 3

        if has_easing_in:
            value -= 1

        if has_easing_out:
            value -= 1

        return Easing(value)

    @classmethod
    def from_easing(cls: Type[EM], easing: Easing) -> EM:
        value = easing.value

        if not value:
            return cls.DEFAULT  # type: ignore

        shift, remainder = divmod((value - 1), 3)
        shift += 2  # in, out
        has_easing_in = remainder != 2
        has_easing_out = remainder != 1

        result = cls(1 << shift)

        if has_easing_in:
            result |= cls.IN  # type: ignore

        if has_easing_out:
            result |= cls.OUT  # type: ignore

        return result


class PulseMode(Enum):
    """An enumeration representing mode of a pulse trigger."""

    COLOR = 0
    HSV = 1

    DEFAULT = COLOR


class ToggleType(Enum):
    SPAWN = 0
    TOGGLE_ON = 1
    TOGGLE_OFF = 2

    DEFAULT = SPAWN


class InstantCountComparison(Enum):
    """An enumeration representing instant count comparison check."""

    EQUALS = 0
    LARGER = 1
    SMALLER = 2

    DEFAULT = EQUALS


class OrbType(Enum):
    """An enumeration representing IDs of orb objects."""

    YELLOW = 36
    BLUE = 84
    PINK = 141
    GREEN = 1022
    RED = 1333
    BLACK = 1330
    DASH = 1704
    REVERSE_DASH = 1751
    TRIGGER = 1594


class PadType(Enum):
    """An enumeration representing IDs of pad objects."""

    YELLOW = 35
    BLUE = 67
    PINK = 140
    RED = 1332


class PickupItemMode(Enum):
    """An enumeration representing mode of a pickup trigger."""

    DEFAULT = 0
    PICKUP = 1
    TOGGLE_TRIGGER = 2


class GameMode(Enum):
    """An enumeration representing different game modes."""

    CUBE = 0
    SHIP = 1
    BALL = 2
    UFO = 3
    WAVE = 4
    ROBOT = 5
    SPIDER = 6
    # SWING_COPTER = 7

    DEFAULT = CUBE


class LevelType(Enum):
    """An enumeration that represents type of the level."""

    NULL = 0
    OFFICIAL = 1
    EDITOR = 2
    SAVED = 3
    ONLINE = 4

    DEFAULT = NULL


class PortalType(Enum):
    """An enumeration representing IDs of portal or speed change objects."""

    CUBE = 12
    SHIP = 13
    BALL = 47
    UFO = 111
    WAVE = 660
    ROBOT = 745
    SPIDER = 1331

    YELLOW_GRAVITY = 11
    BLUE_GRAVITY = 10
    YELLOW_MIRROR = 45
    BLUE_MIRROR = 46
    PINK_SIZE = 101
    GREEN_SIZE = 99
    YELLOW_DUAL = 286
    BLUE_DUAL = 287
    BLUE_TELEPORT = 747
    YELLOW_TELEPORT = 749


class SpeedChange(Enum):
    SLOW = 200
    NORMAL = 201
    FAST = 202
    FASTER = 203
    FASTEST = 1334


class PulseTargetType(Enum):
    """An enumeration representing type of pulse trigger target."""

    COLOR_CHANNEL = 0
    GROUP = 1

    DEFAULT = COLOR_CHANNEL


class PulseType(Flag):
    MAIN = 1
    DETAIL = 2

    BOTH = MAIN | DETAIL

    DEFAULT = BOTH


class SpecialBlockType(Enum):
    """An enumeration representing IDs of special objects (e.g. *S*, *H*, etc)."""

    D = 1755
    J = 1813
    S = 1829
    H = 1859


class SpecialColorID(Enum):
    """An enumeration representing IDs of special colors (e.g. *BG*, *Line*, etc)."""

    BACKGROUND = BG = 1000
    GROUND = G = 1001
    LINE = L = 1002
    LINE_3D = L3D = 1003
    OBJECT = OBJ = 1004
    PLAYER_1 = P1 = 1005
    PLAYER_2 = P2 = 1006
    LIGHT_BACKGROUND = LBG = 1007
    SECONDARY_GROUND = GROUND_2 = G2 = 1009
    BLACK = 1010
    WHITE = 1011
    LIGHTER = 1012


class TargetType(Flag):
    """An enumeration representing modes for a targetted move trigger."""

    NONE = 0

    X = 1
    Y = 2

    BOTH = X | Y

    DEFAULT = NONE


class TouchToggleMode(Enum):
    """An enumeration representing toggle modes of a touch trigger."""

    DEFAULT = 0
    ON = 1
    OFF = 2


class MiscType(Enum):
    """An enumeration representing miscellaneous IDs of objects."""

    TEXT = 914


class TriggerType(Enum):
    """An enumeration representing IDs of most triggers."""

    MOVE = 901
    PULSE = 1006
    ALPHA = 1007
    TOGGLE = 1049
    SPAWN = 1268
    ROTATE = 1346
    FOLLOW = 1347
    SHAKE = 1520
    ANIMATE = 1585
    TOUCH = 1595
    COUNT = 1611
    STOP = 1616
    INSTANT_COUNT = 1811
    ON_DEATH = 1812
    FOLLOW_PLAYER_Y = 1814
    COLLISION = 1815
    PICKUP = 1817


class ZLayer(Flag):
    BOTTOM_4 = B4 = 7
    BOTTOM_3 = B3 = 6
    BOTTOM_2 = B2 = 5
    BOTTOM_1 = B1 = 4

    DEFAULT = D = 0

    TOP_1 = T1 = 1
    TOP_2 = T2 = 2
    TOP_3 = T3 = 3

    def is_default(self) -> bool:
        return self is type(self).DEFAULT


class SimpleZLayer(Enum):
    """An enumeration representing Z Layer of objects."""

    BOTTOM_4 = B4 = -3
    BOTTOM_3 = B3 = -1
    BOTTOM_2 = B2 = 1
    BOTTOM_1 = B1 = 3
    TOP_1 = T1 = 5
    TOP_2 = T2 = 7
    TOP_3 = T3 = 9

    DEFAULT = 0

    BOTTOM = 1
    MIDDLE = 3
    TOP = 5
    VERY_TOP = 7

    ABS_ZERO = 4

    def is_default(self) -> bool:
        return self is type(self).DEFAULT


class Speed(Enum):
    """An enumeration representing speed modifier modes."""

    NORMAL = 0
    SLOW = 1
    FAST = 2
    FASTER = 3
    FASTEST = 4

    DEFAULT = NORMAL


class SpeedConstant(float, Enum):
    """An enumeration representing actual speed modifiers."""

    NULL = 0.0
    SLOW = 0.7
    NORMAL = 0.9
    FAST = 1.1
    FASTER = 1.3
    FASTEST = 1.6


class SpeedMagic(float, Enum):
    """An enumeration of *magic* speed constants."""

    SLOW = 251.16
    NORMAL = 311.58
    FAST = 387.42
    FASTER = 468.0
    FASTEST = 576.0
    DEFAULT = NORMAL


GC = TypeVar("GC", bound="GuidelineColor")


class GuidelineColor(float, Enum):
    """An enumeration representing guideline colors."""

    DEFAULT = 0.0
    TRANSPARENT = 0.7
    ORANGE = 0.8
    YELLOW = 0.9
    GREEN = 1.0

    @classmethod
    def enum_missing(cls: Type[GC], value: float) -> GC:
        if cls.ORANGE < value < cls.GREEN:
            return cls.ORANGE  # type: ignore

        return cls.TRANSPARENT  # type: ignore


class InternalType(Enum):
    LEVEL = 4
    SONG = 6
    CHALLENGE = 7
    REWARD = 8
    REWARD_OBJECT = 9


class Filter(Enum):
    NONE = 0
    DETAIL = 1
    STATIC = 2
    CUSTOM = 3

    DEFAULT = NONE


class Permissions(Flag):
    NONE = 0
    EXECUTE = 1
    WRITE = 2
    READ = 4

    DEFAULT = READ | WRITE | EXECUTE


class ByteOrder(Enum):
    """An enumeration representing byte orders."""

    LITTLE = "<"
    NATIVE = "="
    BIG = ">"

    DEFAULT = LITTLE


class Platform(Enum):
    """An enumeration representing system platforms."""

    UNKNOWN = 0
    ANDROID = 1
    IOS = 2
    IPAD_OS = 3
    LINUX = 4
    MAC_OS = 5
    WINDOWS = 6


class Orientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1

    DEFAULT = HORIZONTAL

    def is_horizontal(self) -> bool:
        return self is type(self).HORIZONTAL

    def is_vertical(self) -> bool:
        return self is type(self).VERTICAL


class ResponseType(Enum):
    BYTES = 0
    TEXT = 1
    JSON = 2

    DEFAULT = TEXT
