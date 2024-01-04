from pathlib import Path
from types import ModuleType as Module

from capnp import load, remove_import_hook  # type: ignore

from gd.string_constants import DOT

__all__ = ()

remove_import_hook()

ROOT = Path(__file__).parent

SUBMODULES_NAME = "submodules"
GD_NAME = "gd"
SCHEMA_NAME = "schema"
SCHEMA = ROOT / SUBMODULES_NAME / SCHEMA_NAME / GD_NAME / SCHEMA_NAME
SCHEMA_SUFFIX = ".capnp"


def load_module(name_path: str, separator: str = DOT, suffix: str = SCHEMA_SUFFIX) -> Module:
    path = SCHEMA

    for name in name_path.split(separator):
        path /= name

    path = path.with_suffix(suffix)

    path_string = path.as_posix()

    if not path.exists():
        raise FileNotFoundError(path_string)

    module = load(path_string)

    return module  # type: ignore


artist = load_module("artist")
comment = load_module("comment")
eitherRecord = load_module("eitherRecord")
eitherReward = load_module("eitherReward")
friendRequest = load_module("friendRequest")
gauntlet = load_module("gauntlet")
mapPack = load_module("mapPack")
level = load_module("level")
message = load_module("message")
password = load_module("password")
song = load_module("song")
user = load_module("user")

ArtistSchema = artist.Artist

CommentLevelReferenceSchema = comment.CommentLevelReference
CommentSchema = comment.Comment

EitherRecordSchema = eitherRecord.EitherRecord

EitherRewardSchema = eitherReward.EitherReward

FriendRequestSchema = friendRequest.FriendRequest

GauntletSchema = gauntlet.Gauntlet

MapPackSchema = mapPack.MapPack

LevelReferenceSchema = level.LevelReference
LevelSchema = level.Level

MessageSchema = message.Message

PasswordSchema = password.Password

SongReferenceSchema = song.SongReference
SongSchema = song.Song

UserReferenceSchema = user.UserReference
UserStatisticsSchema = user.UserStatistics
UserCosmeticsSchema = user.UserCosmetics
UserStatesSchema = user.UserStates
UserSocialsSchema = user.UserSocials
UserLeaderboardSchema = user.UserLeaderboard
UserSchema = user.User

artistApi = load_module("api.artist")
colorChannel = load_module("api.colorChannel")
editor = load_module("api.editor")
folder = load_module("api.folder")
guidelines = load_module("api.guidelines")
header = load_module("api.header")
hsv = load_module("api.hsv")
levelApi = load_module("api.level")
like = load_module("api.like")
object = load_module("api.object")
recording = load_module("api.recording")
songApi = load_module("api.song")
# completed = load_module("api.database.completed")
# database = load_module("api.database.database")
# statistics = load_module("api.database.statistics")
# storage = load_module("api.database.storage")
# unlockValues = load_module("api.database.unlockValues")
# values = load_module("api.database.values")
# variables = load_module("api.database.variables")

ArtistAPISchema = artistApi.ArtistApi

ColorChannelSchema = colorChannel.ColorChannel

EditorSchema = editor.Editor

FolderSchema = folder.Folder

GuidelineSchema = guidelines.Guideline

HeaderSchema = header.Header

HsvSchema = hsv.Hsv

LevelAPISchema = levelApi.LevelApi

LikeSchema = like.Like

ObjectSchema = object.AnyObject

RecordingItemSchema = recording.RecordingItem

SongAPISchema = songApi.SongApi
