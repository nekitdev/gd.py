from gd.api.artist import ArtistAPI
from gd.api.color_channels import (
    ColorChannel,
    ColorChannels,
    CopiedColorChannel,
    NormalColorChannel,
    PlayerColorChannel,
)
from gd.api.database import Database
from gd.api.editor import Editor
from gd.api.folder import Folder
from gd.api.guidelines import Guidelines
from gd.api.header import Header
from gd.api.hsv import HSV
from gd.api.levels import (
    BaseLevelAPI,
    CreatedLevelAPI,
    CustomLevelAPI,
    GauntletLevelAPI,
    OfficialLevelAPI,
    SavedLevelAPI,
    TimelyLevelAPI,
)
from gd.api.like import Like
from gd.api.objects import (
    AlphaTrigger,
    AnimateTrigger,
    CollisionBlock,
    CollisionTrigger,
    ColorTrigger,
    CopiedColorTrigger,
    CountTrigger,
    FollowPlayerYTrigger,
    FollowTrigger,
    GroupIDs,
    InstantCountTrigger,
    Item,
    ItemCounter,
    MoveTrigger,
    NormalColorTrigger,
    NormalMoveTrigger,
    Object,
    OnDeathTrigger,
    Orb,
    PickupItem,
    PickupTrigger,
    PlayerColorTrigger,
    PulsatingObject,
    PulseColorChannelTrigger,
    PulseColorGroupTrigger,
    PulseHSVChannelTrigger,
    PulseHSVGroupTrigger,
    PulseTrigger,
    RotateTrigger,
    RotatingObject,
    SecretCoin,
    ShakeTrigger,
    SpawnTrigger,
    StopTrigger,
    TargetMoveTrigger,
    Teleport,
    Text,
    ToggleItem,
    ToggleTrigger,
    TouchTrigger,
    TriggerOrb,
)
from gd.api.recording import Recording, RecordingItem
from gd.api.rewards import Quest, Reward, RewardItem
from gd.api.save_manager import SaveManager, create_database, save
from gd.api.song import SongAPI

__all__ = (
    # database
    "Database",
    # like
    "Like",
    # folder
    "Folder",
    # rewards
    "Quest",
    "Reward",
    "RewardItem",
    # level API
    "BaseLevelAPI",
    "CreatedLevelAPI",
    "CustomLevelAPI",
    "GauntletLevelAPI",
    "OfficialLevelAPI",
    "SavedLevelAPI",
    "TimelyLevelAPI",
    # editor
    "Editor",
    # header
    "Header",
    # color channels
    "PlayerColorChannel",
    "NormalColorChannel",
    "CopiedColorChannel",
    "ColorChannel",  # union
    "ColorChannels",
    # HSV
    "HSV",
    # groups
    "GroupIDs",
    # objects
    "Object",
    "PulsatingObject",
    "RotatingObject",
    "Orb",
    "TriggerOrb",
    "ItemCounter",
    "SecretCoin",
    "Text",
    "Teleport",
    "ToggleItem",
    "PickupItem",
    "CollisionBlock",
    "PlayerColorTrigger",
    "NormalColorTrigger",
    "CopiedColorTrigger",
    "PulseColorChannelTrigger",
    "PulseHSVChannelTrigger",
    "PulseColorGroupTrigger",
    "PulseHSVGroupTrigger",
    "AlphaTrigger",
    "NormalMoveTrigger",
    "TargetMoveTrigger",
    "SpawnTrigger",
    "StopTrigger",
    "ToggleTrigger",
    "RotateTrigger",
    "FollowTrigger",
    "ShakeTrigger",
    "AnimateTrigger",
    "TouchTrigger",
    "CountTrigger",
    "InstantCountTrigger",
    "PickupTrigger",
    "FollowPlayerYTrigger",
    "OnDeathTrigger",
    "CollisionTrigger",
    # unions
    "Item",
    "ColorTrigger",
    "PulseTrigger",
    "MoveTrigger",
    # guidelines
    "Guidelines",
    # recording
    "Recording",
    "RecordingItem",
    # save manager
    "SaveManager",
    "create_database",
    "save",
    # artist API
    "ArtistAPI",
    # song API
    "SongAPI",
)
