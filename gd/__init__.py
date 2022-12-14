"""An API wrapper for Geometry Dash written in Python."""

__description__ = "An API wrapper for Geometry Dash written in Python."
__url__ = "https://github.com/nekitdev/gd.py"

__title__ = "gd"
__author__ = "nekitdev"
__license__ = "MIT"
__version__ = "1.0.0-alpha.1"

from gd import api, binary, encoding, events, image, json, tasks
from gd.artist import Artist
from gd.binary import BinaryInfo
from gd.client import Client
from gd.color import Color
from gd.comments import Comment, LevelComment, UserComment
from gd.credentials import Credentials
from gd.entity import Entity
from gd.enums import (
    AccountURLType,
    ByteOrder,
    CoinType,
    CollectedCoins,
    CommentState,
    CommentStrategy,
    CommentType,
    CustomParticleGrouping,
    CustomParticleProperty,
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
    Key,
    LeaderboardStrategy,
    LevelDifficulty,
    LevelLeaderboardStrategy,
    LevelLength,
    LevelType,
    LikeType,
    MessageState,
    MessageType,
    OrbType,
    Orientation,
    PadType,
    PickupItemMode,
    Platform,
    PlayerColor,
    PortalType,
    PulseMode,
    PulseTargetType,
    PulseType,
    QuestType,
    RateType,
    RelationshipType,
    ResponseType,
    RewardType,
    Role,
    Salt,
    Scene,
    Score,
    SearchStrategy,
    Secret,
    ShardType,
    SimpleKey,
    SimpleRelationshipType,
    SimpleZLayer,
    SpecialBlockType,
    SpecialColorID,
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
    LevelPrivacy,
    ZLayer,
)
from gd.errors import (
    ClientError,
    CommentBanned,
    GDError,
    HTTPError,
    HTTPErrorWithOrigin,
    HTTPStatusError,
    InternalError,
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
from gd.platform import SYSTEM_PLATFORM
from gd.relationship import Relationship
from gd.rewards import Chest, Quest
from gd.session import Session
from gd.song import Song
from gd.users import LeaderboardUser, LevelLeaderboardUser, User
from gd.version import python_version_info, version_info
from gd.versions import GameVersion, Version

__all__ = (
    # system platform
    "SYSTEM_PLATFORM",
    # versions info
    "version_info",
    "python_version_info",
    # modules
    "api",
    "binary",
    "encoding",
    "events",
    "image",
    "json",
    "tasks",
    # binary info
    "BinaryInfo",
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
    "Comment",
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
    # relationships
    "Relationship",
    # rewards
    "Chest",
    "Quest",
    # songs
    "Song",
    # users
    "User",
    "LeaderboardUser",
    "LevelLeaderboardUser",
    # passwords
    "Password",
    # versions
    "Version",
    "GameVersion",
    # errors
    "InternalError",
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
    "RateType",
    "Score",
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
    "ToggleType",
    "InstantCountComparison",
    "OrbType",
    "PadType",
    "PickupItemMode",
    "GameMode",
    "LevelType",
    "PortalType",
    "SpeedChangeType",
    "CoinType",
    "PulseTargetType",
    "PulseType",
    "SpecialBlockType",
    "SpecialColorID",
    "TargetType",
    "TouchToggleMode",
    "TriggerType",
    "ZLayer",
    "SimpleZLayer",
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
)
