from datetime import timedelta
from typing import Optional, Type, TypeVar

from attrs import define, field
from typing_extensions import Protocol
from yarl import URL

from gd.constants import DEFAULT_ID, DEFAULT_SIZE, EMPTY, UNKNOWN
from gd.models_constants import (
    COMMENT_BANNED_SEPARATOR,
    CREATOR_SEPARATOR,
    DATABASE_SEPARATOR,
    LOGIN_SEPARATOR,
    PAGE_SEPARATOR,
    SONG_SEPARATOR,
)
from gd.models_utils import (
    concat_comment_banned,
    concat_creator,
    concat_login,
    concat_page,
    concat_song,
    float_str,
    split_comment_banned,
    split_creator,
    split_login,
    split_page,
    split_song,
)
from gd.robtop import RobTop

__all__ = (
    "Model",
    "ChestModel",
    "CommentBannedModel",
    "CommentInnerModel",
    "CommentModel",
    "CommentUserModel",
    "CreatorModel",
    "DatabaseModel",
    "FriendRequestModel",
    "GauntletModel",
    "LevelLeaderboardUserModel",
    "LeaderboardUserModel",
    "LevelModel",
    "ListUserModel",
    "LoginModel",
    "MapPackModel",
    "MessageModel",
    "PageModel",
    "ProfileUserModel",
    "QuestModel",
    "SearchUserModel",
    "SongModel",
    "TimelyInfoModel",
)


class Model(RobTop, Protocol):
    """Represents various models."""


SONG_ID = 1
SONG_NAME = 2
SONG_ARTIST_ID = 3
SONG_ARTIST_NAME = 4
SONG_SIZE = 5
SONG_YOUTUBE_VIDEO_ID = 6
SONG_YOUTUBE_CHANNEL_ID = 7
SONG_UNKNOWN = 8
SONG_DOWNLOAD_URL = 10


S = TypeVar("S", bound="SongModel")


@define()
class SongModel(Model):
    id: int = DEFAULT_ID
    name: str = UNKNOWN
    artist_name: str = UNKNOWN
    artist_id: int = DEFAULT_ID
    size: float = DEFAULT_SIZE
    youtube_video_id: str = EMPTY
    youtube_channel_id: str = EMPTY
    unknown: str = EMPTY
    download_url: Optional[URL] = None

    @classmethod
    def from_robtop(
        cls: Type[S],
        string: str,
        *,  # bring indexes and defaults into the scope
        song_id_index: int = SONG_ID,
        song_name_index: int = SONG_NAME,
        song_artist_name_index: int = SONG_ARTIST_NAME,
        song_artist_id_index: int = SONG_ARTIST_ID,
        song_size_index: int = SONG_SIZE,
        song_youtube_video_id_index: int = SONG_YOUTUBE_VIDEO_ID,
        song_youtube_channel_id_index: int = SONG_YOUTUBE_CHANNEL_ID,
        song_unknown_index: int = SONG_UNKNOWN,
        song_download_url_index: int = SONG_DOWNLOAD_URL,
        song_id_default: int = DEFAULT_ID,
        song_name_default: str = UNKNOWN,
        song_artist_name_default: str = UNKNOWN,
        song_artist_id_default: int = DEFAULT_ID,
        song_size_default: float = DEFAULT_SIZE,
        song_youtube_video_id_default: str = EMPTY,
        song_youtube_channel_id_default: str = EMPTY,
        song_unknown_default: str = EMPTY,
        song_download_url_default: str = EMPTY,
    ) -> S:
        mapping = split_song(string)

        download_url = mapping.get(song_download_url_index, song_download_url_default)

        download_url = URL(download_url) if download_url else None

        return cls(
            id=int(mapping.get(song_id_index, song_id_default)),
            name=mapping.get(song_name_index, song_name_default),
            artist_name=mapping.get(song_artist_name_index, song_artist_name_default),
            artist_id=int(mapping.get(song_artist_id_index, song_artist_id_default)),
            size=float(mapping.get(song_size_index, song_size_default)),
            youtube_video_id=mapping.get(
                song_youtube_video_id_index, song_youtube_video_id_default
            ),
            youtube_channel_id=mapping.get(
                song_youtube_channel_id_index, song_youtube_channel_id_default
            ),
            unknown=mapping.get(song_unknown_index, song_unknown_default),
            download_url=download_url,
        )

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return SONG_SEPARATOR in string

    def to_robtop(
        self,
        *,  # bring indexes into the scope
        song_id_index: int = SONG_ID,
        song_name_index: int = SONG_NAME,
        song_artist_name_index: int = SONG_ARTIST_NAME,
        song_artist_id_index: int = SONG_ARTIST_ID,
        song_size_index: int = SONG_SIZE,
        song_youtube_video_id_index: int = SONG_YOUTUBE_VIDEO_ID,
        song_youtube_channel_id_index: int = SONG_YOUTUBE_CHANNEL_ID,
        song_unknown_index: int = SONG_UNKNOWN,
        song_download_url_index: int = SONG_DOWNLOAD_URL,
    ) -> str:
        mapping = {
            song_id_index: str(self.id),
            song_name_index: self.name,
            song_artist_name_index: self.artist_name,
            song_artist_id_index: str(self.artist_id),
            song_size_index: float_str(self.size),
            song_youtube_video_id_index: self.youtube_video_id,
            song_youtube_channel_id_index: self.youtube_channel_id,
            song_unknown_index: self.unknown,
            song_download_url_index: str(self.download_url or EMPTY),
        }

        return concat_song(mapping)


L = TypeVar("L", bound="LoginModel")


@define()
class LoginModel(Model):
    account_id: int = 0
    id: int = 0

    @classmethod
    def from_robtop(cls: Type[L], string: str) -> L:
        account_id, id = split_login(string)

        return cls(int(account_id), int(id))

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LOGIN_SEPARATOR in string

    def to_robtop(self) -> str:
        values = (self.account_id, self.id)

        return concat_login(map(str, values))


C = TypeVar("C", bound="CreatorModel")


@define()
class CreatorModel(Model):
    account_id: int = DEFAULT_ID
    name: str = UNKNOWN
    id: int = DEFAULT_ID

    @classmethod
    def from_robtop(cls: Type[C], string: str) -> C:
        account_id, name, id = split_creator(string)

        return cls(int(account_id), name, int(id))

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return CREATOR_SEPARATOR in string

    def to_robtop(self) -> str:
        values = (self.account_id, self.name, self.id)

        return concat_creator(map(str, values))


@define()
class DatabaseModel(Model):
    main: bytes
    levels: bytes

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return DATABASE_SEPARATOR in string


DEFAULT_TOTAL = 0
DEFAULT_PAGE_START = 0
DEFAULT_PAGE_STOP = 0


P = TypeVar("P", bound="PageModel")


@define()
class PageModel(Model):
    total: int = DEFAULT_TOTAL
    page_start: int = DEFAULT_PAGE_START
    page_stop: int = DEFAULT_PAGE_STOP

    @classmethod
    def from_robtop(cls: Type[P], string: str) -> P:
        total, page_start, page_stop = map(int, split_page(string))

        return cls(total, page_start, page_stop)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return PAGE_SEPARATOR in string

    def to_robtop(self) -> str:
        return concat_page(map(str, (self.total, self.page_start, self.page_stop)))


TEMPORARY = "temp"

B = TypeVar("B", bound="CommentBannedModel")


@define()
class CommentBannedModel(Model):
    string: str = field(default=TEMPORARY)
    timeout: timedelta = field(factory=timedelta)
    reason: str = field(default=EMPTY)

    @classmethod
    def from_robtop(cls: Type[B], string: str) -> B:
        string, timeout, reason = split_comment_banned(string)

        return cls(string, timedelta(seconds=int(timeout)), reason)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return COMMENT_BANNED_SEPARATOR in string

    def to_robtop(self) -> str:
        values = (self.string, str(int(self.timeout.total_seconds())), self.reason)

        return concat_comment_banned(values)
