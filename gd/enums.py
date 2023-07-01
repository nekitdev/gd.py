from __future__ import annotations

from enum import Enum, Flag
from typing import Any, Optional

from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS, EMPTY

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
    "LevelPrivacy",
    "LevelDifficulty",
    "Difficulty",
    "DemonDifficulty",
    "TimelyType",
    "TimelyID",
    "RateFilter",
    "SpecialRateType",
    "RateType",
    "CommentType",
    "RelationshipType",
    "FriendRequestType",
    "MessageType",
    "CommentStrategy",
    "LeaderboardStrategy",
    "LevelLeaderboardStrategy",
    "LikeType",
    "GauntletID",
    "SearchStrategy",
    "RewardType",
    "ChestType",
    "ShardType",
    "RewardItemType",
    "QuestType",
    "Scene",
    "PlayerColor",
    # "CustomParticleGrouping",
    # "CustomParticleProperty",
    "Easing",
    "EasingMethod",
    "PulseMode",
    "ToggleType",
    "InstantCountComparison",
    "OrbType",
    "PadType",
    "MiscType",
    "ItemMode",
    "GameMode",
    "LevelType",
    "PortalType",
    "SpeedChangeType",
    "CoinType",
    "ItemType",
    "RotatingObjectType",
    "PulseTargetType",
    "PulsatingObjectType",
    "PulseType",
    "SpecialBlockType",
    "SpecialColorID",
    "LegacyColorID",
    "LockedType",
    "TargetType",
    "SimpleTargetType",
    "TouchToggleMode",
    "TriggerType",
    "Speed",
    "SpeedConstant",
    "SpeedMagic",
    "GuidelineColor",
    "InternalType",
    "Filter",
    "ByteOrder",
    "Platform",
    "Orientation",
    "ResponseType",
    "CollectedCoins",
    "Quality",
    "Permissions",
)


class SimpleKey(Enum):
    """Represents keys used in static *XOR* ciphers."""

    SAVE = 11


class Key(Enum):
    """Represents keys used in cyclic *XOR* ciphers."""

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


class Salt(Enum):
    """Represents salts used in hashing."""

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
    """Represents secrets."""

    MAIN = "Wmfd2893gb7"
    LEVEL = "Wmfv2898gc9"
    USER = "Wmfv3899gc9"
    MOD = "Wmfp3879gc3"


class AccountURLType(Enum):
    """Represents account URL types."""

    SAVE = 1
    LOAD = 2


class IconType(Enum):
    """Represents icon types."""

    CUBE = 0
    SHIP = 1
    BALL = 2
    UFO = 3
    WAVE = 4
    ROBOT = 5
    SPIDER = 6
    # SWING_COPTER = 7

    DEFAULT = CUBE

    def is_default(self) -> bool:
        return self is type(self).DEFAULT

    def is_cube(self) -> bool:
        return self is type(self).CUBE

    def is_ship(self) -> bool:
        return self is type(self).SHIP

    def is_ball(self) -> bool:
        return self is type(self).BALL

    def is_ufo(self) -> bool:
        return self is type(self).UFO

    def is_wave(self) -> bool:
        return self is type(self).WAVE

    def is_robot(self) -> bool:
        return self is type(self).ROBOT

    def is_spider(self) -> bool:
        return self is type(self).SPIDER

    # def is_swing_copter(self) -> bool:
    #     return self is type(self).SWING_COPTER


class MessageState(Enum):
    """Represents message states."""

    OPEN_TO_ALL = 0
    OPEN_TO_FRIENDS = 1
    CLOSED = 2

    DEFAULT = OPEN_TO_ALL


class CommentState(Enum):
    """Represents comment states."""

    OPEN_TO_ALL = 0
    OPEN_TO_FRIENDS = 1
    CLOSED = 2

    DEFAULT = OPEN_TO_ALL


class FriendState(Enum):
    """Represents friend states."""

    NOT_FRIEND = 0
    FRIEND = 1
    BLOCKED = 2
    OUTGOING_REQUEST = 3
    INCOMING_REQUEST = 4

    DEFAULT = NOT_FRIEND


class FriendRequestState(Enum):
    """Represents friend request states."""

    OPEN = 0
    CLOSED = 1

    DEFAULT = OPEN


class Role(Enum):
    """Represents server roles."""

    USER = 0
    MODERATOR = 1
    ELDER_MODERATOR = 2

    DEFAULT = USER


class LevelLength(Enum):
    """Represents level lengths."""

    TINY = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    XL = 4
    PLATFORMER = 5

    DEFAULT = TINY

    @classmethod
    def _missing_(cls, value: Any) -> Optional[LevelLength]:  # type: ignore
        if value < 0:
            return cls.TINY

        return cls.XL


class LevelPrivacy(Enum):
    """Represents level privacy settings."""

    PUBLIC = 0
    FRIENDS = 1
    PRIVATE = 2

    DEFAULT = PUBLIC

    def is_private(self) -> bool:
        return self is type(self).PRIVATE

    def is_friends(self) -> bool:
        return self is type(self).FRIENDS

    def is_public(self) -> bool:
        return self is type(self).PUBLIC


class Difficulty(Enum):
    """Represents difficulties."""

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

    def into_demon_difficulty(self) -> DemonDifficulty:
        return DIFFICULTY_TO_DEMON_DIFFICULTY[self]

    def is_unknown(self) -> bool:
        return self is type(self).UNKNOWN

    def is_auto(self) -> bool:
        return self is type(self).AUTO

    def is_unspecified_demon(self) -> bool:
        return self is type(self).DEMON

    def is_specified_demon(self) -> bool:
        return self in DEMON

    def is_demon(self) -> bool:
        return self.is_unspecified_demon() or self.is_specified_demon()

    def clamp_demon(self) -> Difficulty:
        if self.is_demon():
            return type(self).DEMON

        return self


DEMON = {
    Difficulty.EASY_DEMON,
    Difficulty.MEDIUM_DEMON,
    Difficulty.HARD_DEMON,
    Difficulty.INSANE_DEMON,
    Difficulty.EXTREME_DEMON,
}


class LevelDifficulty(Enum):
    """Represents level difficulties."""

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
    """Represents demon difficulties."""

    DEMON = 0
    EASY_DEMON = 1
    MEDIUM_DEMON = 2
    HARD_DEMON = 3
    INSANE_DEMON = 4
    EXTREME_DEMON = 5

    DEFAULT = DEMON

    def into_difficulty(self) -> Difficulty:
        return DEMON_DIFFICULTY_TO_DIFFICULTY[self]

    def into_level_difficulty(self) -> LevelDifficulty:
        return DEMON_DIFFICULTY_TO_LEVEL_DIFFICULTY[self]


DEMON_DIFFICULTY_TO_DIFFICULTY = {
    DemonDifficulty.DEMON: Difficulty.DEMON,
    DemonDifficulty.EASY_DEMON: Difficulty.EASY_DEMON,
    DemonDifficulty.MEDIUM_DEMON: Difficulty.MEDIUM_DEMON,
    DemonDifficulty.HARD_DEMON: Difficulty.HARD_DEMON,
    DemonDifficulty.INSANE_DEMON: Difficulty.INSANE_DEMON,
    DemonDifficulty.EXTREME_DEMON: Difficulty.EXTREME_DEMON,
}

DIFFICULTY_TO_DEMON_DIFFICULTY = {
    difficulty: demon_difficulty
    for demon_difficulty, difficulty in DEMON_DIFFICULTY_TO_DIFFICULTY.items()
}


DEMON_DIFFICULTY_TO_LEVEL_DIFFICULTY = {  # because GD handles things like that (?)
    DemonDifficulty.DEMON: LevelDifficulty.DEMON,
    DemonDifficulty.EASY_DEMON: LevelDifficulty.EASY,
    DemonDifficulty.MEDIUM_DEMON: LevelDifficulty.NORMAL,
    DemonDifficulty.HARD_DEMON: LevelDifficulty.HARD,
    DemonDifficulty.INSANE_DEMON: LevelDifficulty.HARDER,
    DemonDifficulty.EXTREME_DEMON: LevelDifficulty.INSANE,
}


class TimelyType(Enum):
    """Represents timely level types."""

    NOT_TIMELY = 0
    DAILY = 1
    WEEKLY = 2
    EVENT = 3

    DEFAULT = NOT_TIMELY

    def into_timely_id(self) -> TimelyID:
        return TIMELY_TYPE_TO_ID[self]

    def is_not_timely(self) -> bool:
        return self is type(self).NOT_TIMELY

    def is_timely(self) -> bool:
        return not self.is_not_timely()

    def is_daily(self) -> bool:
        return self is type(self).DAILY

    def is_weekly(self) -> bool:
        return self is type(self).WEEKLY


class TimelyID(Enum):
    """Represents timely level IDs."""

    NOT_TIMELY = 0
    DAILY = -1
    WEEKLY = -2
    EVENT = -3

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
    TimelyType.EVENT: TimelyID.EVENT,
}

TIMELY_ID_TO_TYPE = {timely_id: timely_type for timely_type, timely_id in TIMELY_TYPE_TO_ID.items()}


class RateFilter(Enum):
    """Represents rate filters."""

    NOT_RATED = 0
    RATED = 1
    FEATURED = 2
    EPIC = 3
    GODLIKE = 4

    def is_not_rated(self) -> bool:
        return self is type(self).NOT_RATED

    def is_rated(self) -> bool:
        return self is type(self).RATED

    def is_featured(self) -> bool:
        return self is type(self).FEATURED

    def is_epic(self) -> bool:
        return self is type(self).EPIC

    def is_godlike(self) -> bool:
        return self is type(self).GODLIKE


class SpecialRateType(Enum):
    """Represents special rate types."""

    NONE = 0
    EPIC = 1
    GODLIKE = 2

    DEFAULT = NONE

    def is_none(self) -> bool:
        return self is type(self).NONE

    def is_epic(self) -> bool:
        return self is type(self).EPIC

    def is_godlike(self) -> bool:
        return self is type(self).GODLIKE

    def is_default(self) -> bool:
        return self is type(self).DEFAULT


class RateType(Flag):
    """Represents rate types."""

    NONE = 0

    NOT_RATED_ONLY = 1 << 0
    RATED_ONLY = 1 << 1
    FEATURED_ONLY = 1 << 2
    EPIC_ONLY = 1 << 3
    GODLIKE_ONLY = 1 << 4

    NOT_RATED = NONE | NOT_RATED_ONLY
    RATED = NOT_RATED | RATED_ONLY
    FEATURED = RATED | FEATURED_ONLY
    EPIC = FEATURED | EPIC_ONLY
    GODLIKE = EPIC | GODLIKE_ONLY

    DEFAULT = NONE

    def is_not_rated(self) -> bool:
        return type(self).NOT_RATED_ONLY in self

    def is_rated(self) -> bool:
        return type(self).RATED_ONLY in self

    def is_featured(self) -> bool:
        return type(self).FEATURED_ONLY in self

    def is_epic(self) -> bool:
        return type(self).EPIC_ONLY in self

    def is_godlike(self) -> bool:
        return type(self).GODLIKE_ONLY in self


class CommentType(Enum):
    """Represents comment types."""

    LEVEL = 0
    USER = 1


class RelationshipType(Enum):
    """Represents relationship types."""

    FRIEND = 0
    BLOCKED = 1

    def is_friend(self) -> bool:
        return self is type(self).FRIEND

    def is_outgoing(self) -> bool:
        return self is type(self).BLOCKED


class FriendRequestType(Enum):
    """Represents friend request types."""

    INCOMING = 0
    OUTGOING = 1

    DEFAULT = INCOMING

    def is_incoming(self) -> bool:
        return self is type(self).INCOMING

    def is_outgoing(self) -> bool:
        return self is type(self).OUTGOING


class MessageType(Enum):
    """Represents message types."""

    INCOMING = 0
    OUTGOING = 1

    DEFAULT = INCOMING

    def is_incoming(self) -> bool:
        return self is type(self).INCOMING

    def is_outgoing(self) -> bool:
        return self is type(self).OUTGOING


class CommentStrategy(Enum):
    """Represents comment strategies."""

    RECENT = 0
    MOST_LIKED = 1

    DEFAULT = RECENT


class LeaderboardStrategy(Enum):
    """Represents leaderboard strategies."""

    PLAYERS = 0
    FRIENDS = 1
    RELATIVE = 2
    CREATORS = 3

    DEFAULT = PLAYERS

    def requires_login(self) -> bool:
        return self in REQUIRES_LOGIN


REQUIRES_LOGIN = {LeaderboardStrategy.FRIENDS, LeaderboardStrategy.RELATIVE}


class LevelLeaderboardStrategy(Enum):
    """Represents level leaderboard strategies."""

    FRIENDS = 0
    ALL = 1
    WEEKLY = 2

    DEFAULT = ALL


class LikeType(Enum):
    """Represents like types."""

    LEVEL = 1
    LEVEL_COMMENT = 2
    USER_COMMENT = 3


class GauntletID(Enum):
    """Represents gauntlet IDs."""

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

    @classmethod
    def _missing_(cls, value: Any) -> GauntletID:  # type: ignore
        return cls.UNKNOWN


class SearchStrategy(Enum):
    """Represents search strategies."""

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
    RATED = 11
    FOLLOWED = 12
    FRIENDS = 13
    MOST_LIKED_WORLD = 15
    HALL_OF_FAME = 16
    FEATURED_WORLD = 17
    UNKNOWN = 18
    DAILY_HISTORY = 21
    WEEKLY_HISTORY = 22

    def is_default(self) -> bool:
        return self is type(self).DEFAULT

    def is_most_downloaded(self) -> bool:
        return self is type(self).MOST_DOWNLOADED

    def is_most_liked(self) -> bool:
        return self is type(self).MOST_LIKED

    def is_trending(self) -> bool:
        return self is type(self).TRENDING

    def is_recent(self) -> bool:
        return self is type(self).RECENT

    def is_by_user(self) -> bool:
        return self is type(self).BY_USER

    def is_featured(self) -> bool:
        return self is type(self).FEATURED

    def is_magic(self) -> bool:
        return self is type(self).MAGIC

    def is_sent(self) -> bool:
        return self is type(self).SENT

    def is_search_many(self) -> bool:
        return self is type(self).SEARCH_MANY

    def is_rated(self) -> bool:
        return self is type(self).RATED

    def is_followed(self) -> bool:
        return self is type(self).FOLLOWED

    def is_friends(self) -> bool:
        return self is type(self).FRIENDS

    def is_most_liked_world(self) -> bool:
        return self is type(self).MOST_LIKED_WORLD

    def is_hall_of_fame(self) -> bool:
        return self is type(self).HALL_OF_FAME

    def is_featured_world(self) -> bool:
        return self is type(self).FEATURED_WORLD

    def is_unknown(self) -> bool:
        return self is type(self).UNKNOWN

    def is_daily_history(self) -> bool:
        return self is type(self).DAILY_HISTORY

    def is_weekly_history(self) -> bool:
        return self is type(self).WEEKLY_HISTORY


class RewardType(Enum):
    """Represents reward types."""

    GET_INFO = 0
    CLAIM_SMALL = 1
    CLAIM_LARGE = 2

    DEFAULT = GET_INFO


class ChestType(Enum):
    """Represents chest types."""

    UNKNOWN = 0

    SMALL = 1
    LARGE = 2

    DEFAULT = UNKNOWN

    def is_small(self) -> bool:
        return self is type(self).SMALL

    def is_large(self) -> bool:
        return self is type(self).LARGE


class ShardType(Enum):
    """Represents shard types."""

    UNKNOWN = 0
    FIRE = 1
    ICE = 2
    POISON = 3
    SHADOW = 4
    LAVA = 5
    NULL = 6

    DEFAULT = UNKNOWN


class RewardItemType(Enum):
    """Represents item types."""

    UNKNOWN = 0

    FIRE_SHARD = 1
    ICE_SHARD = 2
    POISON_SHARD = 3
    SHADOW_SHARD = 4
    LAVA_SHARD = 5
    KEY = 6
    ORB = 7
    DIAMOND = 8
    CUSTOM = 9

    DEFAULT = UNKNOWN

    def is_custom(self) -> bool:
        return self is type(self).CUSTOM


class QuestType(Enum):
    """Represents quest types."""

    UNKNOWN = 0
    ORBS = 1
    COINS = 2
    STARS = 3

    DEFAULT = UNKNOWN

    def is_unknown(self) -> bool:
        return self is type(self).UNKNOWN


class Scene(Enum):
    """Represents various scene IDs."""

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
    """Represents player color settings."""

    NOT_USED = 0

    COLOR_1 = 1
    COLOR_2 = 2

    P1 = COLOR_1
    P2 = COLOR_2

    DEFAULT = NOT_USED

    def is_not_used(self) -> bool:
        return self is type(self).NOT_USED

    def is_used(self) -> bool:
        return not self.is_not_used()

    def is_default(self) -> bool:
        return self is type(self).DEFAULT

    def is_color_1(self) -> bool:
        return self is type(self).COLOR_1

    def is_color_2(self) -> bool:
        return self is type(self).COLOR_2


# class CustomParticleGrouping(Enum):
#     """Represents custom particle grouping types."""

#     FREE = 0
#     RELATIVE = 1
#     GROUPED = 2


# class CustomParticleProperty(Enum):
#     """Represents custom particle properties."""

#     GRAVITY = 0
#     RADIUS = 1


class Easing(Enum):
    """Represents easing types."""

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


IN_OUT_SHIFT = 2
MULTIPLIER = 3

EXPECTED_MODIFIERS = "expected IN and/or OUT modifiers"


class EasingMethod(Flag):
    """Represents easing methods."""

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
            return Easing.NONE

        has_easing_in = cls.IN in self
        has_easing_out = cls.OUT in self

        if not has_easing_in and not has_easing_out:
            raise ValueError(EXPECTED_MODIFIERS)

        value = (value.bit_length() - IN_OUT_SHIFT) * MULTIPLIER

        if has_easing_in:
            value -= 1

        if has_easing_out:
            value -= 1

        return Easing(value)

    @classmethod
    def from_easing(cls, easing: Easing) -> EasingMethod:
        value = easing.value

        if not value:
            return cls.DEFAULT

        IN = cls.IN
        OUT = cls.OUT

        shift, remainder = divmod((value - 1), MULTIPLIER)
        shift += IN_OUT_SHIFT

        has_easing_in = remainder != OUT.value
        has_easing_out = remainder != IN.value

        result = cls(1 << shift)

        if has_easing_in:
            result |= IN

        if has_easing_out:
            result |= OUT

        return result


class PulseMode(Enum):
    """Represents pulse modes."""

    COLOR = 0
    HSV = 1

    DEFAULT = COLOR

    def is_color(self) -> bool:
        return self is type(self).COLOR

    def is_hsv(self) -> bool:
        return self is type(self).HSV


class ToggleType(Enum):
    """Represents toggle types."""

    SPAWN = 0
    TOGGLE_ON = 1
    TOGGLE_OFF = 2

    DEFAULT = SPAWN


class InstantCountComparison(Enum):
    """Represents instant count comparison types."""

    EQUALS = 0
    LARGER = 1
    SMALLER = 2

    DEFAULT = EQUALS


class OrbType(Enum):
    """Represents orb object IDs."""

    YELLOW = 36
    BLUE = 84
    PINK = 141
    GREEN = 1022
    RED = 1333
    BLACK = 1330
    DASH = 1704
    REVERSE_DASH = 1751
    TRIGGER = 1594

    @property
    def id(self) -> int:
        return self.value

    def is_trigger(self) -> int:
        return self is type(self).TRIGGER


class PadType(Enum):
    """Represents pad object IDs."""

    YELLOW = 35
    BLUE = 67
    PINK = 140
    RED = 1332

    @property
    def id(self) -> int:
        return self.value


class MiscType(Enum):
    """Represents miscellaneous object IDs."""

    TEXT = 914
    START_POSITION = 31
    ITEM_COUNTER = 1615
    COLLISION_BLOCK = 1816

    @property
    def id(self) -> int:
        return self.value


class ItemMode(Enum):
    """Represents item modes."""

    DEFAULT = 0
    PICKUP = 1
    TOGGLE = 2

    def is_pickup(self) -> bool:
        return self is type(self).PICKUP

    def is_toggle(self) -> bool:
        return self is type(self).TOGGLE


class GameMode(Enum):
    """Represents game modes."""

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
    """Represents level types."""

    NULL = 0
    OFFICIAL = 1
    CREATED = 2
    SAVED = 3
    ONLINE = 4

    def is_null(self) -> bool:
        return self is type(self).NULL

    def is_official(self) -> bool:
        return self is type(self).OFFICIAL

    def is_created(self) -> bool:
        return self is type(self).CREATED

    def is_saved(self) -> bool:
        return self is type(self).SAVED

    def is_online(self) -> bool:
        return self is type(self).ONLINE

    DEFAULT = NULL


class PortalType(Enum):
    """Represents portal object IDs."""

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

    @property
    def id(self) -> int:
        return self.value


class SpeedChangeType(Enum):
    """Represents speed change object IDs."""

    SLOW = 200
    NORMAL = 201
    FAST = 202
    FASTER = 203
    FASTEST = 1334

    @property
    def id(self) -> int:
        return self.value


class CoinType(Enum):
    """Represents coin object IDs."""

    SECRET = 142
    USER = 1329

    @property
    def id(self) -> int:
        return self.value


class ItemType(Enum):
    """Represents pickup item object IDs."""

    KEY = 1275
    HEART = 1587
    BOTTLE = 1589
    SKULL = 1598
    COIN = 1614

    @property
    def id(self) -> int:
        return self.value


class RotatingObjectType(Enum):
    """Represents rotating object IDs."""

    ID_85 = 85
    ID_86 = 86
    ID_87 = 87
    ID_97 = 97

    ID_137 = 137
    ID_138 = 138
    ID_139 = 139

    ID_154 = 154
    ID_155 = 155
    ID_156 = 156

    ID_180 = 180
    ID_181 = 181
    ID_182 = 182

    ID_183 = 183
    ID_184 = 184
    ID_185 = 185

    ID_186 = 186
    ID_187 = 187
    ID_188 = 188

    ID_222 = 222
    ID_223 = 223
    ID_224 = 224

    ID_375 = 375
    ID_376 = 376
    ID_377 = 377
    ID_378 = 378

    ID_394 = 394
    ID_395 = 395
    ID_396 = 396

    ID_678 = 678
    ID_679 = 679
    ID_680 = 680

    ID_740 = 740
    ID_741 = 741
    ID_742 = 742

    ID_997 = 997
    ID_998 = 998
    ID_999 = 999
    ID_1000 = 1000

    ID_1019 = 1019
    ID_1020 = 1020
    ID_1021 = 1021

    ID_1055 = 1055
    ID_1056 = 1056
    ID_1057 = 1057

    ID_1058 = 1058
    ID_1059 = 1059
    ID_1060 = 1060
    ID_1061 = 1061

    ID_1521 = 1521
    ID_1522 = 1522
    ID_1523 = 1523
    ID_1524 = 1524

    ID_1525 = 1525
    ID_1526 = 1526
    ID_1527 = 1527
    ID_1528 = 1528

    ID_1582 = 1582

    ID_1619 = 1619
    ID_1620 = 1620

    ID_1705 = 1705
    ID_1706 = 1706
    ID_1707 = 1707

    ID_1708 = 1708
    ID_1709 = 1709
    ID_1710 = 1710

    ID_1734 = 1734
    ID_1735 = 1735
    ID_1736 = 1736

    ID_1752 = 1752

    ID_1831 = 1831
    ID_1832 = 1832

    ID_1833 = 1833
    ID_1834 = 1834

    @property
    def id(self) -> int:
        return self.value


class PulseTargetType(Enum):
    """Represents pulse target types."""

    COLOR_CHANNEL = 0
    GROUP = 1

    DEFAULT = COLOR_CHANNEL

    def is_color_channel(self) -> bool:
        return self is type(self).COLOR_CHANNEL

    def is_group(self) -> bool:
        return self is type(self).GROUP


class PulsatingObjectType(Enum):
    """Represents pulsating object IDs."""

    OUTER_LARGE = 1839
    OUTER_SMALL = 1840
    INNER_LARGE = 1841
    INNER_SMALL = 1842

    @property
    def id(self) -> int:
        return self.value


class PulseType(Flag):
    """Represents pulse types."""

    MAIN = 1
    DETAIL = 2

    BOTH = MAIN | DETAIL

    DEFAULT = BOTH

    def is_main_only(self) -> bool:
        return self is type(self).MAIN

    def is_detail_only(self) -> bool:
        return self is type(self).DETAIL


class SpecialBlockType(Enum):
    """Represents special block (`D`, `J`, `S`, `H`) object IDs."""

    D = 1755
    J = 1813
    S = 1829
    H = 1859


class SpecialColorID(Enum):
    """Represents special color IDs."""

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

    @property
    def id(self) -> int:
        return self.value


class LegacyColorID(Enum):
    DEFAULT = 0
    PLAYER_1 = 1
    PLAYER_2 = 2
    COLOR_1 = 3
    COLOR_2 = 4
    LIGHT_BACKGROUND = 5
    COLOR_3 = 6
    COLOR_4 = 7
    LINE_3D = 8

    def migrate(self) -> int:
        return LEGACY_COLOR_ID_TO_COLOR_ID[self]


LEGACY_COLOR_ID_TO_COLOR_ID = {
    LegacyColorID.DEFAULT: 0,
    LegacyColorID.PLAYER_1: SpecialColorID.PLAYER_1.id,
    LegacyColorID.PLAYER_2: SpecialColorID.PLAYER_2.id,
    LegacyColorID.COLOR_1: 1,
    LegacyColorID.COLOR_2: 2,
    LegacyColorID.LIGHT_BACKGROUND: SpecialColorID.LIGHT_BACKGROUND.id,
    LegacyColorID.COLOR_3: 3,
    LegacyColorID.COLOR_4: 4,
    LegacyColorID.LINE_3D: SpecialColorID.LINE_3D.id,
}


class LockedType(Flag):
    NONE = 0

    X = 1
    Y = 2

    BOTH = X | Y

    DEFAULT = NONE

    def x(self) -> bool:
        return type(self).X in self

    def y(self) -> bool:
        return type(self).Y in self


class TargetType(Flag):
    """Represents move target types."""

    NONE = 0

    X = 1
    Y = 2

    BOTH = X | Y

    DEFAULT = NONE

    def is_none(self) -> bool:
        return self is type(self).NONE

    def into_simple_target_type(self) -> SimpleTargetType:
        return TARGET_TYPE_TO_SIMPLE_TARGET_TYPE[self]


class SimpleTargetType(Enum):
    """Represents simple move target types."""

    BOTH = 0

    X_ONLY = 1
    Y_ONLY = 2

    DEFAULT = BOTH

    def into_target_type(self) -> TargetType:
        return SIMPLE_TARGET_TYPE_TO_TARGET_TYPE[self]


TARGET_TYPE_TO_SIMPLE_TARGET_TYPE = {
    TargetType.BOTH: SimpleTargetType.BOTH,
    TargetType.X: SimpleTargetType.X_ONLY,
    TargetType.Y: SimpleTargetType.Y_ONLY,
}

SIMPLE_TARGET_TYPE_TO_TARGET_TYPE = {
    simple_target_type: target_type
    for target_type, simple_target_type in TARGET_TYPE_TO_SIMPLE_TARGET_TYPE.items()
}


class TouchToggleMode(Enum):
    """Represents touch toggle modes."""

    DEFAULT = 0
    ON = 1
    OFF = 2


class TriggerType(Enum):
    """Represents trigger object IDs."""

    BACKGROUND = BG = 29
    GROUND = G = 30
    LINE = L = 104
    OBJECT = OBJ = 105
    COLOR_1 = C1 = 221
    COLOR_2 = C2 = 717
    COLOR_3 = C3 = 718
    COLOR_4 = C4 = 743
    LINE_3D = L3D = 744
    COLOR = 899
    SECONDARY_GROUND = GROUND_2 = G2 = 900
    MOVE = 901
    # LINE_2 = L2 = 915
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

    @property
    def id(self) -> int:
        return self.value


class Speed(Enum):
    """Represents speed modifiers."""

    NORMAL = 0
    SLOW = 1
    FAST = 2
    FASTER = 3
    FASTEST = 4

    DEFAULT = NORMAL


class SpeedConstant(float, Enum):
    """Represents actuall speed modifiers."""

    NULL = 0.0
    SLOW = 0.7
    NORMAL = 0.9
    FAST = 1.1
    FASTER = 1.3
    FASTEST = 1.6


class SpeedMagic(float, Enum):
    """Represents *magic* speed constants."""

    SLOW = 251.16
    NORMAL = 311.58
    FAST = 387.42
    FASTER = 468.0
    FASTEST = 576.0
    DEFAULT = NORMAL


class GuidelineColor(float, Enum):
    """Represents guideline colors."""

    DEFAULT = 0.0
    TRANSPARENT = 0.7
    ORANGE = 0.8
    YELLOW = 0.9
    GREEN = 1.0

    @classmethod
    def _missing_(cls, value: Any) -> GuidelineColor:  # type: ignore
        if cls.ORANGE < value < cls.GREEN:
            return cls.ORANGE

        return cls.TRANSPARENT


class InternalType(Enum):
    """Represents internal types."""

    LEVEL = 4
    SONG = 6
    QUEST = 7
    REWARD_ITEM = 8
    REWARD = 9


class Filter(Enum):
    """Represents filter types."""

    NONE = 0
    DETAIL = 1
    STATIC = 2
    CUSTOM = 3

    DEFAULT = NONE

    def is_none(self) -> bool:
        return self is type(self).NONE

    def is_detail(self) -> bool:
        return self is type(self).DETAIL

    def is_static(self) -> bool:
        return self is type(self).STATIC

    def is_custom(self) -> bool:
        return self is type(self).CUSTOM

    def is_default(self) -> bool:
        return self is type(self).DEFAULT


class ByteOrder(Enum):
    """Represents byte orders (used in binary protocols)."""

    NATIVE = "="
    LITTLE = "<"
    BIG = ">"

    DEFAULT = LITTLE

    def is_native(self) -> bool:
        return self is type(self).NATIVE

    def is_little(self) -> bool:
        return self is type(self).LITTLE

    def is_big(self) -> bool:
        return self is type(self).BIG

    def is_default(self) -> bool:
        return self is type(self).DEFAULT


class Platform(Enum):
    """Represents system platforms."""

    UNKNOWN = 0

    ANDROID = 1
    DARWIN = 2
    LINUX = 3
    WINDOWS = 4

    DEFAULT = UNKNOWN

    def is_unknown(self) -> bool:
        return self is type(self).UNKNOWN

    def is_android(self) -> bool:
        return self is type(self).ANDROID

    def is_darwin(self) -> bool:
        return self is type(self).DARWIN

    def is_linux(self) -> bool:
        return self is type(self).LINUX

    def is_windows(self) -> bool:
        return self is type(self).WINDOWS


class Orientation(Enum):
    """Represents orientations."""

    HORIZONTAL = 0
    VERTICAL = 1

    DEFAULT = HORIZONTAL

    def is_horizontal(self) -> bool:
        return self is type(self).HORIZONTAL

    def is_vertical(self) -> bool:
        return self is type(self).VERTICAL


class ResponseType(Enum):
    """Represents response types."""

    BYTES = 0
    TEXT = 1
    JSON = 2

    DEFAULT = TEXT


class CollectedCoins(Flag):
    """Represents collected coins."""

    NONE = 0

    FIRST = 1
    SECOND = 2
    THIRD = 4

    ALL = FIRST | SECOND | THIRD

    DEFAULT = NONE

    def first(self) -> bool:
        return type(self).FIRST in self

    def second(self) -> bool:
        return type(self).SECOND in self

    def third(self) -> bool:
        return type(self).THIRD in self

    def all(self) -> bool:
        return type(self).ALL in self


class Quality(Enum):
    """Represents quality settings."""

    AUTO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    DEFAULT = AUTO


class Permissions(Flag):
    """Represents permissions."""

    NONE = 0

    EXECUTE = 1
    WRITE = 2
    READ = 4

    ALL = EXECUTE | WRITE | READ

    DEFAULT = ALL
