from datetime import timedelta
from functools import partial
from typing import List, Optional, Type, TypeVar
from urllib.parse import quote, unquote

from attrs import define, field
from typing_extensions import Protocol
from yarl import URL

from gd.constants import DEFAULT_ACTIVE, DEFAULT_COLOR_1_ID, DEFAULT_COLOR_2_ID, DEFAULT_CREATOR_POINTS, DEFAULT_DEMONS, DEFAULT_DIAMONDS, DEFAULT_GLOW, DEFAULT_ICON_ID, DEFAULT_ID, DEFAULT_NEW, DEFAULT_RANK, DEFAULT_SECRET_COINS, DEFAULT_SIZE, DEFAULT_STARS, DEFAULT_USER_COINS, EMPTY, UNKNOWN
from gd.enums import CommentState, FriendRequestState, FriendState, IconType, MessageState, Role
from gd.models_constants import (
    COMMENT_BANNED_SEPARATOR,
    CREATOR_SEPARATOR,
    DATABASE_SEPARATOR,
    LOGIN_SEPARATOR,
    PAGE_SEPARATOR,
    SEARCH_USER_SEPARATOR,
    SEARCH_USERS_RESPONSE_SEPARATOR,
    SONG_SEPARATOR,
)
from gd.models_utils import (
    concat_comment_banned,
    concat_creator,
    concat_login,
    concat_page,
    concat_search_user,
    concat_search_users_response,
    concat_search_users_response_users,
    concat_song,
    float_str,
    int_bool,
    parse_get_or,
    partial_parse_enum,
    split_comment_banned,
    split_creator,
    split_login,
    split_page,
    split_search_user,
    split_search_users_response,
    split_search_users_response_users,
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
        # indexes
        song_id_index: int = SONG_ID,
        song_name_index: int = SONG_NAME,
        song_artist_name_index: int = SONG_ARTIST_NAME,
        song_artist_id_index: int = SONG_ARTIST_ID,
        song_size_index: int = SONG_SIZE,
        song_youtube_video_id_index: int = SONG_YOUTUBE_VIDEO_ID,
        song_youtube_channel_id_index: int = SONG_YOUTUBE_CHANNEL_ID,
        song_unknown_index: int = SONG_UNKNOWN,
        song_download_url_index: int = SONG_DOWNLOAD_URL,
        # defaults
        song_id_default: int = DEFAULT_ID,
        song_name_default: str = UNKNOWN,
        song_artist_name_default: str = UNKNOWN,
        song_artist_id_default: int = DEFAULT_ID,
        song_size_default: float = DEFAULT_SIZE,
        song_youtube_video_id_default: str = EMPTY,
        song_youtube_channel_id_default: str = EMPTY,
        song_unknown_default: str = EMPTY,
    ) -> S:
        mapping = split_song(string)

        download_url_string = mapping.get(song_download_url_index)

        download_url = URL(download_url_string) if download_url_string else None

        return cls(
            id=parse_get_or(int, song_id_default, mapping.get(song_id_index)),
            name=mapping.get(song_name_index, song_name_default),
            artist_name=mapping.get(song_artist_name_index, song_artist_name_default),
            artist_id=parse_get_or(int, song_artist_id_default, mapping.get(song_artist_id_index)),
            size=parse_get_or(float, song_size_default, mapping.get(song_size_index)),
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
            song_download_url_index: quote(str(self.download_url or EMPTY)),
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
DEFAULT_START = 0
DEFAULT_STOP = 0


A = TypeVar("A", bound="PageModel")


@define()
class PageModel(Model):
    total: int = DEFAULT_TOTAL
    start: int = DEFAULT_START
    stop: int = DEFAULT_STOP

    @classmethod
    def from_robtop(cls: Type[A], string: str) -> A:
        total, start, stop = map(int, split_page(string))

        return cls(total, start, stop)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return PAGE_SEPARATOR in string

    def to_robtop(self) -> str:
        return concat_page(map(str, (self.total, self.start, self.stop)))


SEARCH_USER_NAME = 1
SEARCH_USER_ID = 2
SEARCH_USER_STARS = 3
SEARCH_USER_DEMONS = 4
SEARCH_USER_RANK = 6
SEARCH_USER_CREATOR_POINTS = 8
SEARCH_USER_ICON_ID = 9
SEARCH_USER_COLOR_1_ID = 10
SEARCH_USER_COLOR_2_ID = 11
SEARCH_USER_SECRET_COINS = 13
SEARCH_USER_ICON_TYPE = 14
SEARCH_USER_GLOW = 15
SEARCH_USER_ACCOUNT_ID = 16
SEARCH_USER_USER_COINS = 17


SU = TypeVar("SU", bound="SearchUserModel")


@define()
class SearchUserModel(Model):
    name: str = UNKNOWN
    id: int = DEFAULT_ID
    stars: int = DEFAULT_STARS
    demons: int = DEFAULT_DEMONS
    rank: int = DEFAULT_RANK
    creator_points: int = DEFAULT_CREATOR_POINTS
    icon_id: int = DEFAULT_ID
    color_1_id: int = DEFAULT_COLOR_1_ID
    color_2_id: int = DEFAULT_COLOR_2_ID
    secret_coins: int = DEFAULT_SECRET_COINS
    icon_type: IconType = IconType.DEFAULT
    glow: bool = DEFAULT_GLOW
    account_id: int = DEFAULT_ID
    user_coins: int = DEFAULT_USER_COINS

    @classmethod
    def from_robtop(
        cls: Type[SU],
        string: str,
        # indexes
        search_user_name_index: int = SEARCH_USER_NAME,
        search_user_id_index: int = SEARCH_USER_ID,
        search_user_stars_index: int = SEARCH_USER_STARS,
        search_user_demons_index: int = SEARCH_USER_DEMONS,
        search_user_rank_index: int = SEARCH_USER_RANK,
        search_user_creator_points_index: int = SEARCH_USER_CREATOR_POINTS,
        search_user_icon_id_index: int = SEARCH_USER_ICON_ID,
        search_user_color_1_id_index: int = SEARCH_USER_COLOR_1_ID,
        search_user_color_2_id_index: int = SEARCH_USER_COLOR_2_ID,
        search_user_secret_coins_index: int = SEARCH_USER_SECRET_COINS,
        search_user_icon_type_index: int = SEARCH_USER_ICON_TYPE,
        search_user_glow_index: int = SEARCH_USER_GLOW,
        search_user_account_id_index: int = SEARCH_USER_ACCOUNT_ID,
        search_user_user_coins_index: int = SEARCH_USER_USER_COINS,
        # defaults
        search_user_name_default: str = UNKNOWN,
        search_user_id_default: int = DEFAULT_ID,
        search_user_stars_default: int = DEFAULT_STARS,
        search_user_demons_default: int = DEFAULT_DEMONS,
        search_user_rank_default: int = DEFAULT_RANK,
        search_user_creator_points_default: int = DEFAULT_CREATOR_POINTS,
        search_user_icon_id_default: int = DEFAULT_ID,
        search_user_color_1_id_default: int = DEFAULT_COLOR_2_ID,
        search_user_color_2_id_default: int = DEFAULT_COLOR_2_ID,
        search_user_secret_coins_default: int = DEFAULT_SECRET_COINS,
        search_user_icon_type_default: IconType = IconType.DEFAULT,
        search_user_glow_default: bool = DEFAULT_GLOW,
        search_user_account_id_default: int = DEFAULT_ID,
        search_user_user_coins_default: int = DEFAULT_USER_COINS,
    ) -> SU:
        mapping = split_search_user(string)

        rank_string = mapping.get(search_user_rank_index)

        if rank_string:
            rank = int(rank_string)

        else:
            rank = search_user_rank_default

        return cls(
            name=mapping.get(search_user_name_index, search_user_name_default),
            id=parse_get_or(int, search_user_id_default, mapping.get(search_user_id_index)),
            stars=parse_get_or(
                int, search_user_stars_default, mapping.get(search_user_stars_index)
            ),
            demons=parse_get_or(
                int, search_user_demons_default, mapping.get(search_user_demons_index)
            ),
            rank=rank,
            creator_points=parse_get_or(
                int, search_user_creator_points_default, mapping.get(search_user_creator_points_index)
            ),
            icon_id=parse_get_or(
                int, search_user_icon_id_default, mapping.get(search_user_icon_id_index)
            ),
            color_1_id=parse_get_or(
                int, search_user_color_1_id_default, mapping.get(search_user_color_1_id_index)
            ),
            color_2_id=parse_get_or(
                int, search_user_color_2_id_default, mapping.get(search_user_color_2_id_index)
            ),
            secret_coins=parse_get_or(
                int, search_user_secret_coins_default, mapping.get(search_user_secret_coins_index)
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                search_user_icon_type_default,
                mapping.get(search_user_icon_type_index),
            ),
            glow=parse_get_or(
                int_bool, search_user_glow_default, mapping.get(search_user_glow_index)
            ),
            account_id=parse_get_or(
                int, search_user_account_id_default, mapping.get(search_user_account_id_index)
            ),
            user_coins=parse_get_or(
                int, search_user_user_coins_default, mapping.get(search_user_user_coins_index)
            ),
        )

    def to_robtop(
        self,
        search_user_name_index: int = SEARCH_USER_NAME,
        search_user_id_index: int = SEARCH_USER_ID,
        search_user_stars_index: int = SEARCH_USER_STARS,
        search_user_demons_index: int = SEARCH_USER_DEMONS,
        search_user_rank_index: int = SEARCH_USER_RANK,
        search_user_creator_points_index: int = SEARCH_USER_CREATOR_POINTS,
        search_user_icon_id_index: int = SEARCH_USER_ICON_ID,
        search_user_color_1_id_index: int = SEARCH_USER_COLOR_1_ID,
        search_user_color_2_id_index: int = SEARCH_USER_COLOR_2_ID,
        search_user_secret_coins_index: int = SEARCH_USER_SECRET_COINS,
        search_user_icon_type_index: int = SEARCH_USER_ICON_TYPE,
        search_user_glow_index: int = SEARCH_USER_GLOW,
        search_user_account_id_index: int = SEARCH_USER_ACCOUNT_ID,
        search_user_user_coins_index: int = SEARCH_USER_USER_COINS,
    ) -> str:
        glow = int(self.glow)

        if glow:
            glow += 1

        mapping = {
            search_user_name_index: self.name,
            search_user_id_index: str(self.id),
            search_user_stars_index: str(self.stars),
            search_user_demons_index: str(self.demons),
            search_user_rank_index: str(self.rank),
            search_user_creator_points_index: str(self.creator_points),
            search_user_icon_id_index: str(self.icon_id),
            search_user_color_1_id_index: str(self.color_1_id),
            search_user_color_2_id_index: str(self.color_2_id),
            search_user_secret_coins_index: str(self.secret_coins),
            search_user_icon_type_index: str(self.icon_type.value),
            search_user_glow_index: str(glow),
            search_user_account_id_index: str(self.account_id),
            search_user_user_coins_index: str(self.user_coins),
        }

        return concat_search_user(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return SEARCH_USER_SEPARATOR in string


PROFILE_NAME = 1
PROFILE_ID = 2
PROFILE_STARS = 3
PROFILE_DEMONS = 4
PROFILE_CREATOR_POINTS = 8
PROFILE_COLOR_1_ID = 10
PROFILE_COLOR_2_ID = 11
PROFILE_SECRET_COINS = 13
PROFILE_ACCOUNT_ID = 16
PROFILE_USER_COINS = 17
PROFILE_MESSAGE_STATE = 18
PROFILE_FRIEND_REQUEST_STATE = 19
PROFILE_YOUTUBE = 20
PROFILE_CUBE_ID = 21
PROFILE_SHIP_ID = 22
PROFILE_BALL_ID = 23
PROFILE_UFO_ID = 24
PROFILE_WAVE_ID = 25
PROFILE_ROBOT_ID = 26
PROFILE_GLOW = 28
PROFILE_ACTIVE = 29
PROFILE_RANK = 30
PROFILE_FRIEND_STATE = 31
PROFILE_NEW_MESSAGES = 38
PROFILE_NEW_FRIEND_REQUESTS = 39
PROFILE_NEW_FRIENDS = 40
PROFILE_SPIDER_ID = 43
PROFILE_TWITTER = 44
PROFILE_TWITCH = 45
PROFILE_DIAMONDS = 46
PROFILE_EXPLOSION_ID = 48
PROFILE_ROLE = 49
PROFILE_COMMENT_STATE = 50


P = TypeVar("P", bound="ProfileModel")


@define()
class ProfileModel(Model):
    @classmethod
    def from_robtop(
        cls: Type[P],
        string: str,
        # indexes
        profile_name_index: int = PROFILE_NAME,
        profile_id_index: int = PROFILE_ID,
        profile_stars_index: int = PROFILE_STARS,
        profile_demons_index: int = PROFILE_DEMONS,
        profile_creator_points_index: int = PROFILE_CREATOR_POINTS,
        profile_color_1_id_index: int = PROFILE_COLOR_1_ID,
        profile_color_2_id_index: int = PROFILE_COLOR_2_ID,
        profile_secret_coins_index: int = PROFILE_SECRET_COINS,
        profile_account_id_index: int = PROFILE_ACCOUNT_ID,
        profile_user_coins_index: int = PROFILE_USER_COINS,
        profile_message_state_index: int = PROFILE_MESSAGE_STATE,
        profile_friend_request_state_index: int = PROFILE_FRIEND_REQUEST_STATE,
        profile_youtube_index: int = PROFILE_YOUTUBE,
        profile_cube_id_index: int = PROFILE_CUBE_ID,
        profile_ship_id_index: int = PROFILE_SHIP_ID,
        profile_ball_id_index: int = PROFILE_BALL_ID,
        profile_ufo_id_index: int = PROFILE_UFO_ID,
        profile_wave_id_index: int = PROFILE_WAVE_ID,
        profile_robot_id_index: int = PROFILE_ROBOT_ID,
        profile_glow_index: int = PROFILE_GLOW,
        profile_active_index: int = PROFILE_ACTIVE,
        profile_rank_index: int = PROFILE_RANK,
        profile_friend_state_index: int = PROFILE_FRIEND_STATE,
        profile_new_messages_index: int = PROFILE_NEW_MESSAGES,
        profile_new_friend_requests_index: int = PROFILE_NEW_FRIEND_REQUESTS,
        profile_new_friends_index: int = PROFILE_NEW_FRIENDS,
        profile_spider_id_index: int = PROFILE_SPIDER_ID,
        profile_twitter_index: int = PROFILE_TWITTER,
        profile_twitch_index: int = PROFILE_TWITCH,
        profile_diamonds_index: int = PROFILE_DIAMONDS,
        profile_explosion_id_index: int = PROFILE_EXPLOSION_ID,
        profile_role_index: int = PROFILE_ROLE,
        profile_comment_state_index: int = PROFILE_COMMENT_STATE,
        # defaults
        profile_name_default: str = UNKNOWN,
        profile_id_default: int = DEFAULT_ID,
        profile_stars_default: int = DEFAULT_STARS,
        profile_demons_default: int = DEFAULT_DEMONS,
        profile_creator_points_default: int = DEFAULT_CREATOR_POINTS,
        profile_color_1_id_default: int = DEFAULT_COLOR_1_ID,
        profile_color_2_id_default: int = DEFAULT_COLOR_2_ID,
        profile_secret_coins_default: int = DEFAULT_SECRET_COINS,
        profile_account_id_default: int = DEFAULT_ID,
        profile_user_coins_default: int = DEFAULT_USER_COINS,
        profile_message_state_default: MessageState = MessageState.DEFAULT,
        profile_friend_request_state_default: FriendRequestState = FriendRequestState.DEFAULT,
        profile_youtube_default: Optional[str] = None,
        profile_cube_id_default: int = DEFAULT_ICON_ID,
        profile_ship_id_default: int = DEFAULT_ICON_ID,
        profile_ball_id_default: int = DEFAULT_ICON_ID,
        profile_ufo_id_default: int = DEFAULT_ICON_ID,
        profile_wave_id_default: int = DEFAULT_ICON_ID,
        profile_robot_id_default: int = DEFAULT_ICON_ID,
        profile_glow_default: bool = DEFAULT_GLOW,
        profile_active_default: bool = DEFAULT_ACTIVE,
        profile_rank_default: int = DEFAULT_RANK,
        profile_friend_state_default: FriendState = FriendState.DEFAULT,
        profile_new_messages_default: int = DEFAULT_NEW,
        profile_new_friend_requests_default: int = DEFAULT_NEW,
        profile_new_friends_default: int = DEFAULT_NEW,
        profile_spider_id_default: int = DEFAULT_ICON_ID,
        profile_twitter_default: Optional[str] = None,
        profile_twitch_default: Optional[str] = None,
        profile_diamonds_default: int = DEFAULT_DIAMONDS,
        profile_explosion_id_default: int = DEFAULT_ICON_ID,
        profile_role_default: Role = Role.DEFAULT,
        profile_comment_state_default: CommentState = CommentState.DEFAULT,
    ) -> P:
        ...

    def to_robtop(
        self,
        profile_name_index: int = PROFILE_NAME,
        profile_id_index: int = PROFILE_ID,
        profile_stars_index: int = PROFILE_STARS,
        profile_demons_index: int = PROFILE_DEMONS,
        profile_creator_points_index: int = PROFILE_CREATOR_POINTS,
        profile_color_1_id_index: int = PROFILE_COLOR_1_ID,
        profile_color_2_id_index: int = PROFILE_COLOR_2_ID,
        profile_secret_coins_index: int = PROFILE_SECRET_COINS,
        profile_account_id_index: int = PROFILE_ACCOUNT_ID,
        profile_user_coins_index: int = PROFILE_USER_COINS,
        profile_message_state_index: int = PROFILE_MESSAGE_STATE,
        profile_friend_request_state_index: int = PROFILE_FRIEND_REQUEST_STATE,
        profile_youtube_index: int = PROFILE_YOUTUBE,
        profile_cube_id_index: int = PROFILE_CUBE_ID,
        profile_ship_id_index: int = PROFILE_SHIP_ID,
        profile_ball_id_index: int = PROFILE_BALL_ID,
        profile_ufo_id_index: int = PROFILE_UFO_ID,
        profile_wave_id_index: int = PROFILE_WAVE_ID,
        profile_robot_id_index: int = PROFILE_ROBOT_ID,
        profile_glow_index: int = PROFILE_GLOW,
        profile_active_index: int = PROFILE_ACTIVE,
        profile_rank_index: int = PROFILE_RANK,
        profile_friend_state_index: int = PROFILE_FRIEND_STATE,
        profile_new_messages_index: int = PROFILE_NEW_MESSAGES,
        profile_new_friend_requests_index: int = PROFILE_NEW_FRIEND_REQUESTS,
        profile_new_friends_index: int = PROFILE_NEW_FRIENDS,
        profile_spider_id_index: int = PROFILE_SPIDER_ID,
        profile_twitter_index: int = PROFILE_TWITTER,
        profile_twitch_index: int = PROFILE_TWITCH,
        profile_diamonds_index: int = PROFILE_DIAMONDS,
        profile_explosion_id_index: int = PROFILE_EXPLOSION_ID,
        profile_role_index: int = PROFILE_ROLE,
        profile_comment_state_index: int = PROFILE_COMMENT_STATE,
    ) -> str:
        ...

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        ...


SUR = TypeVar("SUR", bound="SearchUsersResponseModel")


@define()
class SearchUsersResponseModel(Model):
    users: List[SearchUserModel] = field(factory=list)
    pages: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[SUR], string: str) -> SUR:
        users_string, pages_string = split_search_users_response(string)

        users = [
            SearchUserModel.from_robtop(string)
            for string in split_search_users_response_users(users_string)
        ]

        pages = PageModel.from_robtop(pages_string)

        return cls(users=users, pages=pages)

    def to_robtop(self) -> str:
        values = (
            concat_search_users_response_users(user.to_robtop() for user in self.users),
            self.pages.to_robtop(),
        )

        return concat_search_users_response(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return SEARCH_USERS_RESPONSE_SEPARATOR in string


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
