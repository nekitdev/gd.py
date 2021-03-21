import enums  # type: ignore

from gd.decorators import patch
from gd.typing import Dict, Optional, Set, TypeVar

__all__ = (
    "JSON",
    "Enum",
    "Flag",
    "Key",
    "Salt",
    "Secret",
    "AccountURLType",
    "IconType",
    "MessageState",
    "CommentState",
    "FriendRequestState",
    "Role",
    "LevelLength",
    "LevelDifficulty",
    "DemonDifficulty",
    "TimelyType",
    "CommentType",
    "MessageType",
    "FriendRequestType",
    "CommentStrategy",
    "LeaderboardStrategy",
    "LevelLeaderboardStrategy",
    "LikeType",
    "SearchStrategy",
    "GauntletID",
    "RewardType",
    "ShardType",
    "QuestType",
    "RelationshipType",
    "SimpleRelationshipType",
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
    "PortalType",
    "SpeedChange",
    "PickupItemMode",
    "PulseType",
    "SpecialBlockType",
    "SpecialColorID",
    "TargetPosCoordinates",
    "TouchToggleMode",
    "TriggerType",
    "ZLayer",
    "MiscType",
    "Gamemode",
    "LevelType",
    "Speed",
    "SpeedConstant",
    "SpeedMagic",
    "GuidelineColor",
    "InternalType",
    "Protection",
    "ByteOrder",
)

UPPER_TITLE: Set[str] = {"NA", "UFO", "XL"}

T = TypeVar("T")


@patch(enums.EnumMeta, "__getattr__")
def __meta_getattr__(cls, name: str) -> enums.Enum:
    try:
        return cls.from_name(name)

    except KeyError:
        raise AttributeError(name) from None


class JSON(enums.Trait):
    def __json__(self) -> Dict[str, T]:
        return {"name": self.title, "value": self.value}


class BetterTitle(enums.Trait):
    @property
    def title(self) -> str:
        name = self.name
        title = super().title

        if name in UPPER_TITLE:
            return title.upper()

        return title


class Enum(enums.StrFormat, enums.Order, JSON, enums.Enum):
    """Normalized generic enum that has ordering and string formatting."""

    pass


class Flag(enums.StrFormat, enums.Order, JSON, enums.Flag):
    """Normalized generic flag that has ordering and string formatting."""

    pass


class Key(Enum):
    """An enumeration for keys used in ciphering."""

    MESSAGE = 14251
    QUESTS = 19847
    LEVEL_PASSWORD = 26364
    COMMENT = 29481
    ACCOUNT_PASSWORD = 37526
    LEVEL_LEADERBOARD = 39673
    LEVEL = 41274
    LIKE_RATE = 58281
    CHESTS = 59182
    USER_LEADERBOARD = 85271

    def __init__(self, value: int) -> None:
        self.string = str(value)
        self.bytes = self.string.encode("utf-8")


class Salt(Enum):
    """An enumeration for salts used in hashing."""

    LEVEL = "xI25fpAapCQg"
    COMMENT = "xPT6iUrtws0J"
    LIKE_RATE = "ysg6pUrtjn0J"
    USER_LEADERBOARD = "xI35fsAapCRg"
    LEVEL_LEADERBOARD = "yPg6pUrtWn0J"
    QUESTS = "oC36fpYaPtdg"
    CHESTS = "pC26fpYaQCtg"
    EMPTY = ""

    def __init__(self, string: str) -> None:
        self.string = string
        self.bytes = string.encode("utf-8")


class Secret(Enum):
    """An enumeration for request secrets."""

    MAIN = "Wmfd2893gb7"
    LEVEL = "Wmfv2898gc9"
    LOGIN = "Wmfv3899gc9"
    MOD = "Wmfp3879gc3"


class AccountURLType(Enum):
    """An enumeration for Account URL types."""

    UNKNOWN = 0
    SAVE = 1
    LOAD = 2


class IconType(BetterTitle, Enum):
    """An enumeration of icon types."""

    CUBE = 0
    SHIP = 1
    BALL = 2
    UFO = 3
    WAVE = 4
    ROBOT = 5
    SPIDER = 6


class MessageState(Enum):
    """An enumeration for message state."""

    OPEN_TO_ALL = 0
    OPEN_TO_FRIENDS_ONLY = 1
    CLOSED = 2


class CommentState(Enum):
    """An enumeration for comment state."""

    OPEN_TO_ALL = 0
    OPEN_TO_FRIENDS_ONLY = 1
    CLOSED = 2


class FriendState(Enum):
    """An enumeration for friend state."""

    NOT_FRIEND = 0
    FRIEND = 1
    OUTGOING_REQUEST = 3
    INCOMING_REQUEST = 4


class FriendRequestState(Enum):
    """An enumeration for friend request state."""

    OPEN = 0
    CLOSED = 1


class Role(Enum):
    """An enumeration for Geometry Dash Status."""

    USER = 0
    MODERATOR = 1
    ELDER_MODERATOR = 2


class LevelLength(BetterTitle, Enum):
    """An enumeration for level lengths."""

    NA = -1
    TINY = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    XL = 4
    EXTRA_LONG = XL

    UNKNOWN = NA

    @classmethod
    def enum_missing(cls, value: int) -> Optional["LevelLength"]:
        if value > cls.XL.value:  # type: ignore
            return cls.XL  # type: ignore

        if value < cls.TINY.value:  # type: ignore
            return cls.TINY  # type: ignore

        return None


class LevelDifficulty(BetterTitle, Enum):
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


class DemonDifficulty(BetterTitle, Enum):
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


class FriendRequestType(Enum):
    """An enumeration for friend request objects."""

    INCOMING = 0
    OUTGOING = 1

    INBOX = INCOMING
    SENT = OUTGOING


class MessageType(Enum):
    """An enumeration for message objects."""

    INCOMING = 0
    OUTGOING = 1

    INBOX = INCOMING
    SENT = OUTGOING


class CommentStrategy(Enum):
    """An enumeration for comment searching."""

    RECENT = 0
    MOST_LIKED = 1


class LeaderboardStrategy(Enum):
    """An enumeration for getting leaderboard users."""

    TOP = 0
    PLAYERS = 0
    FRIENDS = 1
    RELATIVE = 2
    CREATORS = 3

    def requires_login(self) -> bool:
        cls = self.__class__

        return self is cls.FRIENDS or self is cls.RELATIVE


class LevelLeaderboardStrategy(Enum):
    """An enumeration for getting level leaderboard."""

    FRIENDS = 0
    ALL = 1
    WEEKLY = 2


class LikeType(Enum):
    """An enumeration for sending ratings for entities."""

    LEVEL = 1
    LEVEL_COMMENT = 2
    COMMENT = 3


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


class RelationshipType(Enum):
    FRIEND = 1
    BLOCKED = 2
    INCOMING_REQUEST = 3
    OUTGOING_REQUEST = 4


class SimpleRelationshipType(Enum):
    FRIEND = 0
    BLOCKED = 1

    FRIENDS = FRIEND


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


class PlayerColor(Enum):
    """An enumeration for player color setting."""

    NOT_USED = -1
    DEFAULT = 0
    P1 = 1
    P2 = 2


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
    """An enumeration representing easing of a moving object (used in move/rotate triggers)."""

    DEFAULT = 0
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


class EasingMethod(Flag):
    DEFAULT = 0
    IN = 1
    OUT = 2
    EASE = 4
    ELASTIC = 8
    BOUNCE = 16
    EXPONENTIAL = 32
    SINE = 64
    BACK = 128

    def as_easing(self) -> Easing:
        cls, value = self.__class__, self.value

        if not value:
            return Easing.DEFAULT  # type: ignore

        has_easing_in = cls.IN in self
        has_easing_out = cls.OUT in self

        if not has_easing_in and not has_easing_out:
            raise ValueError(f"{self!r} does not have In/Out modifiers.")

        value = (value.bit_length() - 2) * 3

        if has_easing_in:
            value -= 1

        if has_easing_out:
            value -= 1

        return Easing(value)

    @classmethod
    def from_easing(cls, easing: Easing) -> Flag:
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


class InstantCountComparison(Enum):
    """An enumeration representing instant count comparison check."""

    EQUALS = 0
    LARGER = 1
    SMALLER = 2


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


class Gamemode(BetterTitle, Enum):
    """An enumeration representing different game modes."""

    CUBE = 0
    SHIP = 1
    BALL = 2
    UFO = 3
    WAVE = 4
    ROBOT = 5
    SPIDER = 6
    # SWING_COPTER = 7


class LevelType(Enum):
    """An enumeration that represents type of the level."""

    NULL = 0
    OFFICIAL = 1
    EDITOR = 2
    SAVED = 3
    ONLINE = 4


class PortalType(BetterTitle, Enum):
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


class PulseType(Enum):
    """An enumeration representing type of pulse trigger target."""

    COLOR_CHANNEL = 0
    GROUP = 1


class SpecialBlockType(Enum):
    """An enumeration representing IDs of special objects (e.g. *S*, *H*, etc)."""

    D = 1755
    J = 1813
    S = 1829
    H = 1859


class SpecialColorID(Enum):
    """An enumeration representing IDs of special colors (e.g. *BG*, *Line*, etc)."""

    BACKGROUND = BG = 1000
    GROUND = GRND = G = 1001
    LINE = L = 1002
    LINE3D = L3D = 1003
    OBJECT = Obj = 1004
    PLAYE1 = P1 = 1005
    PLAYER2 = P2 = 1006
    LIGHT_BACKGROUND = LBG = 1007
    GROUND2 = GRND2 = G2 = 1009
    BLACK = 1010
    WHITE = 1011
    LIGHTER = 1012


class TargetPosCoordinates(Enum):
    """An enumeration representing modes for a targetted move trigger."""

    BOTH = 0
    ONLY_X = 1
    ONLY_Y = 2


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

    BACKGROUND = BG = 29
    GROUND = GRND = G = 30
    START_POS = 31
    ENABLE_TRAIL = 32
    DISABLE_TRAIL = 33
    LINE = L = 104
    OBJECT = OBJ = 105
    COLOR1 = 221
    COLOR2 = 717
    COLOR3 = 718
    COLOR4 = 743
    LINE3D = L3D = 744
    COLOR = 899
    GROUND2 = GRND2 = G2 = 900
    MOVE = 901
    LINE2 = 915
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
    HIDE_PLAYER = 1612
    SHOW_PLAYER = 1613
    STOP = 1616
    INSTANT_COUNT = 1811
    ON_DEATH = 1812
    FOLLOW_PLAYER_Y = 1814
    COLLISION = 1815
    PICKUP = 1817
    BG_EFFECT_ON = 1818
    BG_EFFECT_OFF = 1819

    RANDOM = 1912
    ZOOM = 1913
    STATIC_CAMERA = 1914
    CAMERA_OFFSET = 1916
    REVERSE = 1917
    END = 1931
    STOP_JUMP = 1932
    SCALE = -11
    SONG = -12
    TIME_WARP = -13


class ZLayer(Enum):
    """An enumeration representing Z Layer of objects."""

    B4 = -3
    B3 = -1
    B2 = 1
    B1 = 3
    T1 = 5
    T2 = 7
    T3 = 9

    BOTTOM = 1
    MIDDLE = 3
    TOP = 5
    HIGHER_TOP = 7
    ABS_ZERO = 4


class Speed(Enum):
    """An enumeration representing speed modifier modes."""

    NORMAL = 0  # x 1
    SLOW = 1  # x 0.5
    FAST = 2  # x 2
    FASTER = 3  # x 3
    FASTEST = 4  # x 4


class SpeedConstant(float, Enum):
    """An enumeration representing actual speed modifiers."""

    NULL = 0.0
    SLOW = 0.7
    NORMAL = 0.9
    FAST = 1.1
    FASTER = 1.3
    FASTEST = 1.6


class SpeedMagic(float, Enum):
    """An enumeration with *magic* speed constants.

    *Magic* constants are used for translating distance travelled (in units)
    with certain speed to time taken, like so:

    .. code-block:: python3

        speed = SpeedMagic.FAST.value  # * 2 speed (well, actually just 1.1 lol)

        x1 = 0  # beginning of the level
        x2 = 1000  # some random coordinate

        dx = x2 - x1

        t = dx / speed  # ~ 2.58
        print(t)
    """

    SLOW = 251.16  # x 0.5
    NORMAL = 311.58  # x 1
    FAST = 387.42  # x 2
    FASTER = 468.0  # x 3
    FASTEST = 576.0  # x 4
    DEFAULT = NORMAL  # -> x 1


class GuidelineColor(float, Enum):
    """An enumeration representing guidelines colors."""

    DEFAULT = 0.0
    TRANSPARENT = 0.7
    ORANGE = 0.8
    YELLOW = 0.9
    GREEN = 1.0

    @classmethod
    def enum_missing(cls, value: float) -> Optional["GuidelineColor"]:
        try:
            if 0.8 < value < 1.0:
                return cls.ORANGE  # type: ignore

            return cls.TRANSPARENT  # type: ignore

        except TypeError:
            return None


class InternalType(Enum):
    LEVEL = 4
    SONG = 6
    CHALLENGE = 7
    REWARD = 8
    REWARD_OBJECT = 9


class Protection(Flag):
    NONE = 0
    READ = 1
    WRITE = 2
    EXECUTE = 4

    R = READ
    W = WRITE
    X = EXECUTE
    E = EXECUTE


class ByteOrder(Enum):
    LITTLE = "<"
    NATIVE = "="
    BIG = ">"


class Platform(Enum):
    UNKNOWN = 0
    ANDROID = 1
    IOS = 2
    LINUX = 3
    MACOS = 4
    WINDOWS = 5
