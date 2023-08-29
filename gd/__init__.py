"""An API wrapper for Geometry Dash written in Python."""

__description__ = "An API wrapper for Geometry Dash written in Python."
__url__ = "https://github.com/nekitdev/gd.py"

__title__ = "gd"
__author__ = "nekitdev"
__license__ = "MIT"
__version__ = "1.0.1"

from gd import (
    api,
    binary,
    encoding,
    events,
    image,
    memory,
    models,
    named_dicts,
    robtop,
    server,
    tasks,
)
from gd.artist import Artist
from gd.binary import BinaryInfo
from gd.binary_utils import Reader, Writer
from gd.capacity import Capacity
from gd.client import Client
from gd.color import Color
from gd.comments import LevelComment, UserComment
from gd.converter import CONVERTER
from gd.credentials import Credentials
from gd.entity import Entity
from gd.enums import (
    AccountURLType,
    ByteOrder,
    ChestType,
    CoinType,
    CollectedCoins,
    CommentState,
    CommentStrategy,
    CommentType,
    DemonDifficulty,
    Difficulty,
    Easing,
    EasingMethod,
    Filter,
    FriendRequestState,
    FriendRequestType,
    FriendState,
    GameMode,
    GauntletID,
    GuidelineColor,
    IconType,
    InstantCountComparison,
    InternalType,
    ItemMode,
    ItemType,
    Key,
    LeaderboardStrategy,
    LegacyColorID,
    LevelDifficulty,
    LevelLeaderboardStrategy,
    LevelLength,
    LevelPrivacy,
    LevelType,
    LikeType,
    LockedType,
    MessageState,
    MessageType,
    MiscType,
    OrbType,
    Orientation,
    PadType,
    Permissions,
    Platform,
    PlayerColor,
    PortalType,
    PulsatingObjectType,
    PulseMode,
    PulseTargetType,
    PulseType,
    Quality,
    QuestType,
    RateFilter,
    RateType,
    RelationshipType,
    ResponseType,
    RewardItemType,
    RewardType,
    Role,
    RotatingObjectType,
    Salt,
    Scene,
    SearchStrategy,
    Secret,
    ShardType,
    SimpleKey,
    SimpleTargetType,
    SpecialBlockType,
    SpecialColorID,
    SpecialRateType,
    Speed,
    SpeedChangeType,
    SpeedConstant,
    SpeedMagic,
    TargetType,
    TimelyID,
    TimelyType,
    ToggleType,
    TouchToggleMode,
    TriggerType,
)
from gd.errors import (
    ClientError,
    CommentBanned,
    GDError,
    HTTPError,
    HTTPErrorWithOrigin,
    HTTPStatusError,
    LoginFailed,
    LoginRequired,
    MissingAccess,
    NothingFound,
    SongRestricted,
)
from gd.filters import Filters
from gd.friend_request import FriendRequest
from gd.http import HTTPClient
from gd.level import Level
from gd.level_packs import Gauntlet, MapPack
from gd.message import Message
from gd.password import Password
from gd.platform import SYSTEM_BITS, SYSTEM_PLATFORM, SYSTEM_PLATFORM_CONFIG
from gd.progress import Progress
from gd.rewards import Chest, Quest
from gd.session import Session
from gd.song import Song
from gd.users import User, UserCosmetics, UserLeaderboard, UserSocials, UserStates, UserStatistics
from gd.version import python_version_info, version_info
from gd.versions import GameVersion, RobTopVersion

__all__ = (
    # system configuration
    "SYSTEM_BITS",
    "SYSTEM_PLATFORM",
    "SYSTEM_PLATFORM_CONFIG",
    # versions info
    "version_info",
    "python_version_info",
    # modules
    "api",
    "binary",
    "encoding",
    "events",
    "image",
    "named_dicts",
    "memory",
    "models",
    "robtop",
    "server",
    "tasks",
    # binary info
    "BinaryInfo",
    # reader & writer
    "Reader",
    "Writer",
    # converter
    "CONVERTER",
    # colors
    "Color",
    # client
    "Client",
    # session
    "Session",
    # HTTP client
    "HTTPClient",
    # models
    "Entity",
    # artists
    "Artist",
    # comments
    "UserComment",
    "LevelComment",
    # credentials
    "Credentials",
    # filters
    "Filters",
    # friend requests
    "FriendRequest",
    # levels
    "Level",
    # level packs
    "Gauntlet",
    "MapPack",
    # messages
    "Message",
    # rewards
    "Chest",
    "Quest",
    # song
    "Song",
    # users
    "User",
    "UserStatistics",
    "UserCosmetics",
    "UserStates",
    "UserSocials",
    "UserLeaderboard",
    # passwords
    "Password",
    # versions
    "RobTopVersion",
    "GameVersion",
    # capacity
    "Capacity",
    # progress
    "Progress",
    # enums
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
    # errors
    "GDError",
    "HTTPError",
    "HTTPErrorWithOrigin",
    "HTTPStatusError",
    "ClientError",
    "MissingAccess",
    "SongRestricted",
    "CommentBanned",
    "LoginFailed",
    "LoginRequired",
    "NothingFound",
)
