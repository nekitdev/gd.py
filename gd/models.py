from datetime import datetime, timedelta
from typing import List, Optional, Type, TypeVar
from urllib.parse import quote, unquote

from attrs import define, field
from typing_extensions import Protocol
from yarl import URL

from gd.constants import (
    DEFAULT_ACTIVE,
    DEFAULT_COLOR_1_ID,
    DEFAULT_COLOR_2_ID,
    DEFAULT_CONTENT_PRESENT,
    DEFAULT_CREATOR_POINTS,
    DEFAULT_DEMONS,
    DEFAULT_DIAMONDS,
    DEFAULT_GLOW,
    DEFAULT_ICON_ID,
    DEFAULT_ID,
    DEFAULT_NEW,
    DEFAULT_PLACE,
    DEFAULT_RANK,
    DEFAULT_READ,
    DEFAULT_SECRET_COINS,
    DEFAULT_SENT,
    DEFAULT_SIZE,
    DEFAULT_STARS,
    DEFAULT_UNREAD,
    DEFAULT_USER_COINS,
    EMPTY,
    UNKNOWN,
)
from gd.datetime import datetime_from_human, datetime_to_human
from gd.encoding import (
    decode_base64_string_url_safe,
    decode_robtop_string,
    encode_base64_string_url_safe,
    encode_robtop_string,
)
from gd.enums import (
    CommentState,
    FriendRequestState,
    FriendState,
    IconType,
    Key,
    MessageState,
    Role,
    TimelyType,
)
from gd.models_constants import (
    COMMENT_BANNED_SEPARATOR,
    CREATOR_SEPARATOR,
    DATABASE_SEPARATOR,
    LEADERBOARD_RESPONSE_USERS_SEPARATOR,
    LEADERBOARD_USER_SEPARATOR,
    LOGIN_SEPARATOR,
    MESSAGE_SEPARATOR,
    MESSAGES_RESPONSE_SEPARATOR,
    PAGE_SEPARATOR,
    PROFILE_SEPARATOR,
    RELATIONSHIP_USER_SEPARATOR,
    RELATIONSHIPS_RESPONSE_USERS_SEPARATOR,
    SEARCH_USER_SEPARATOR,
    SEARCH_USERS_RESPONSE_SEPARATOR,
    SONG_SEPARATOR,
    TIMELY_INFO_SEPARATOR,
)
from gd.models_utils import (
    concat_comment_banned,
    concat_creator,
    concat_leaderboard_response_users,
    concat_leaderboard_user,
    concat_login,
    concat_message,
    concat_messages_response,
    concat_messages_response_messages,
    concat_page,
    concat_profile,
    concat_relationship_user,
    concat_relationships_response_users,
    concat_search_user,
    concat_search_users_response,
    concat_search_users_response_users,
    concat_song,
    concat_timely_info,
    float_str,
    int_bool,
    parse_get_or,
    partial_parse_enum,
    split_comment_banned,
    split_creator,
    split_leaderboard_response_users,
    split_leaderboard_user,
    split_login,
    split_message,
    split_messages_response,
    split_messages_response_messages,
    split_page,
    split_profile,
    split_relationship_user,
    split_relationships_response_users,
    split_search_user,
    split_search_users_response,
    split_search_users_response_users,
    split_song,
    split_timely_info,
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
    "LoginModel",
    "MapPackModel",
    "MessageModel",
    "PageModel",
    "ProfileModel",
    "QuestModel",
    "RelationshipUserModel",
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

        download_url = URL(unquote(download_url_string)) if download_url_string else None

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


DEFAULT_START = 0
DEFAULT_STOP = 0


A = TypeVar("A", bound="PageModel")


@define()
class PageModel(Model):
    total: Optional[int] = None
    start: int = DEFAULT_START
    stop: int = DEFAULT_STOP

    @classmethod
    def from_robtop(cls: Type[A], string: str) -> A:
        try:
            total, start, stop = map(int, split_page(string))

        except ValueError:
            start, stop = map(int, split_page(string))

            total = None

        return cls(total, start, stop)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return PAGE_SEPARATOR in string

    def to_robtop(self) -> str:
        total = self.total
        start = self.start
        stop = self.stop

        if total is None:
            values = (start, stop)

        else:
            values = (total, start, stop)

        return concat_page(map(str, values))


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
                int,
                search_user_creator_points_default,
                mapping.get(search_user_creator_points_index),
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
        glow = self.glow
        glow += glow

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
    name: str = UNKNOWN
    id: int = DEFAULT_ID
    stars: int = DEFAULT_STARS
    demons: int = DEFAULT_DEMONS
    creator_points: int = DEFAULT_CREATOR_POINTS
    color_1_id: int = DEFAULT_COLOR_1_ID
    color_2_id: int = DEFAULT_COLOR_2_ID
    secret_coins: int = DEFAULT_SECRET_COINS
    account_id: int = DEFAULT_ID
    user_coins: int = DEFAULT_USER_COINS
    message_state: MessageState = MessageState.DEFAULT
    friend_request_state: FriendRequestState = FriendRequestState.DEFAULT
    youtube: Optional[str] = None
    cube_id: int = DEFAULT_ICON_ID
    ship_id: int = DEFAULT_ICON_ID
    ball_id: int = DEFAULT_ICON_ID
    ufo_id: int = DEFAULT_ICON_ID
    wave_id: int = DEFAULT_ICON_ID
    robot_id: int = DEFAULT_ICON_ID
    glow: bool = DEFAULT_GLOW
    active: bool = DEFAULT_ACTIVE
    rank: int = DEFAULT_RANK
    friend_state: FriendState = FriendState.DEFAULT
    new_messages: int = DEFAULT_NEW
    new_friend_requests: int = DEFAULT_NEW
    new_friends: int = DEFAULT_NEW
    spider_id: int = DEFAULT_ICON_ID
    twitter: Optional[str] = None
    twitch: Optional[str] = None
    diamonds: int = DEFAULT_DIAMONDS
    explosion_id: int = DEFAULT_ICON_ID
    role: Role = Role.DEFAULT
    comment_state: CommentState = CommentState.DEFAULT

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
        mapping = split_profile(string)

        return cls(
            name=mapping.get(profile_name_index, profile_name_default),
            id=parse_get_or(int, profile_id_default, mapping.get(profile_id_index)),
            stars=parse_get_or(int, profile_stars_default, mapping.get(profile_stars_index)),
            demons=parse_get_or(int, profile_demons_default, mapping.get(profile_demons_index)),
            creator_points=parse_get_or(
                int, profile_creator_points_default, mapping.get(profile_creator_points_index)
            ),
            color_1_id=parse_get_or(
                int, profile_color_1_id_default, mapping.get(profile_color_1_id_index)
            ),
            color_2_id=parse_get_or(
                int, profile_color_2_id_default, mapping.get(profile_color_2_id_index)
            ),
            secret_coins=parse_get_or(
                int, profile_secret_coins_default, mapping.get(profile_secret_coins_index)
            ),
            account_id=parse_get_or(
                int, profile_account_id_default, mapping.get(profile_account_id_index)
            ),
            user_coins=parse_get_or(
                int, profile_user_coins_default, mapping.get(profile_user_coins_index)
            ),
            message_state=parse_get_or(
                partial_parse_enum(int, MessageState),
                profile_message_state_default,
                mapping.get(profile_message_state_index),
            ),
            friend_request_state=parse_get_or(
                partial_parse_enum(int, FriendRequestState),
                profile_friend_request_state_default,
                mapping.get(profile_friend_request_state_index),
            ),
            youtube=mapping.get(profile_youtube_index) or profile_youtube_default,
            cube_id=parse_get_or(int, profile_cube_id_default, mapping.get(profile_cube_id_index)),
            ship_id=parse_get_or(int, profile_ship_id_default, mapping.get(profile_ship_id_index)),
            ball_id=parse_get_or(int, profile_ball_id_default, mapping.get(profile_ball_id_index)),
            ufo_id=parse_get_or(int, profile_ufo_id_default, mapping.get(profile_ufo_id_index)),
            wave_id=parse_get_or(int, profile_wave_id_default, mapping.get(profile_wave_id_index)),
            robot_id=parse_get_or(
                int, profile_robot_id_default, mapping.get(profile_robot_id_index)
            ),
            glow=parse_get_or(int_bool, profile_glow_default, mapping.get(profile_glow_index)),
            active=parse_get_or(
                int_bool, profile_active_default, mapping.get(profile_active_index)
            ),
            rank=parse_get_or(int, profile_rank_default, mapping.get(profile_rank_index)),
            friend_state=parse_get_or(
                partial_parse_enum(int, FriendState),
                profile_friend_state_default,
                mapping.get(profile_friend_state_index),
            ),
            new_messages=parse_get_or(
                int, profile_new_messages_default, mapping.get(profile_new_messages_index)
            ),
            new_friend_requests=parse_get_or(
                int,
                profile_new_friend_requests_default,
                mapping.get(profile_new_friend_requests_index),
            ),
            new_friends=parse_get_or(
                int, profile_new_friends_default, mapping.get(profile_new_friends_index)
            ),
            spider_id=parse_get_or(
                int, profile_spider_id_default, mapping.get(profile_spider_id_index)
            ),
            twitter=mapping.get(profile_twitter_index) or profile_twitter_default,
            twitch=mapping.get(profile_twitch_index) or profile_twitch_default,
            diamonds=parse_get_or(
                int, profile_diamonds_default, mapping.get(profile_diamonds_index)
            ),
            explosion_id=parse_get_or(
                int, profile_explosion_id_default, mapping.get(profile_explosion_id_index)
            ),
            role=parse_get_or(
                partial_parse_enum(int, Role), profile_role_default, mapping.get(profile_role_index)
            ),
            comment_state=parse_get_or(
                partial_parse_enum(int, CommentState),
                profile_comment_state_default,
                mapping.get(profile_comment_state_index),
            ),
        )

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
        mapping = {
            profile_name_index: self.name,
            profile_id_index: str(self.id),
            profile_stars_index: str(self.stars),
            profile_demons_index: str(self.demons),
            profile_creator_points_index: str(self.creator_points),
            profile_color_1_id_index: str(self.color_1_id),
            profile_color_2_id_index: str(self.color_2_id),
            profile_secret_coins_index: str(self.secret_coins),
            profile_account_id_index: str(self.account_id),
            profile_user_coins_index: str(self.user_coins),
            profile_message_state_index: str(self.message_state.value),
            profile_friend_request_state_index: str(self.friend_request_state.value),
            profile_youtube_index: self.youtube or EMPTY,
            profile_cube_id_index: str(self.cube_id),
            profile_ship_id_index: str(self.ship_id),
            profile_ball_id_index: str(self.ball_id),
            profile_ufo_id_index: str(self.ufo_id),
            profile_wave_id_index: str(self.wave_id),
            profile_robot_id_index: str(self.robot_id),
            profile_glow_index: str(int(self.glow)),
            profile_active_index: str(int(self.active)),
            profile_rank_index: str(int(self.rank)),
            profile_friend_state_index: str(self.friend_state.value),
            profile_new_messages_index: str(self.new_messages),
            profile_new_friend_requests_index: str(self.new_friend_requests),
            profile_new_friends_index: str(self.new_friends),
            profile_spider_id_index: str(self.spider_id),
            profile_twitter_index: self.twitter or EMPTY,
            profile_twitch_index: self.twitch or EMPTY,
            profile_diamonds_index: str(self.diamonds),
            profile_explosion_id_index: str(self.explosion_id),
            profile_role_index: str(self.role.value),
            profile_comment_state_index: str(self.comment_state.value),
        }

        return concat_profile(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return PROFILE_SEPARATOR in string

    @property
    def banned(self) -> bool:
        return not self.active

    @banned.setter
    def banned(self, banned: bool) -> None:
        self.active = not self.banned


RELATIONSHIP_USER_NAME = 1
RELATIONSHIP_USER_ID = 2
RELATIONSHIP_USER_ICON_ID = 9
RELATIONSHIP_USER_COLOR_1_ID = 10
RELATIONSHIP_USER_COLOR_2_ID = 11
RELATIONSHIP_USER_ICON_TYPE = 14
RELATIONSHIP_USER_GLOW = 15
RELATIONSHIP_USER_ACCOUNT_ID = 16
RELATIONSHIP_USER_MESSAGE_STATE = 18


RU = TypeVar("RU", bound="RelationshipUserModel")


@define()
class RelationshipUserModel(Model):
    name: str = UNKNOWN
    id: int = DEFAULT_ID
    icon_id: int = DEFAULT_ICON_ID
    color_1_id: int = DEFAULT_COLOR_1_ID
    color_2_id: int = DEFAULT_COLOR_2_ID
    icon_type: IconType = IconType.DEFAULT
    glow: bool = DEFAULT_GLOW
    account_id: int = DEFAULT_ID
    message_state: MessageState = MessageState.DEFAULT

    @classmethod
    def from_robtop(
        cls: Type[RU],
        string: str,
        relationship_user_name_index: int = RELATIONSHIP_USER_NAME,
        relationship_user_id_index: int = RELATIONSHIP_USER_ID,
        relationship_user_icon_id_index: int = RELATIONSHIP_USER_ICON_ID,
        relationship_user_color_1_id_index: int = RELATIONSHIP_USER_COLOR_1_ID,
        relationship_user_color_2_id_index: int = RELATIONSHIP_USER_COLOR_2_ID,
        relationship_user_icon_type_index: int = RELATIONSHIP_USER_ICON_TYPE,
        relationship_user_glow_index: int = RELATIONSHIP_USER_GLOW,
        relationship_user_account_id_index: int = RELATIONSHIP_USER_ACCOUNT_ID,
        relationship_user_message_state_index: int = RELATIONSHIP_USER_MESSAGE_STATE,
        relationship_user_name_default: str = UNKNOWN,
        relationship_user_id_default: int = DEFAULT_ID,
        relationship_user_icon_id_default: int = DEFAULT_ICON_ID,
        relationship_user_color_1_id_default: int = DEFAULT_COLOR_1_ID,
        relationship_user_color_2_id_default: int = DEFAULT_COLOR_2_ID,
        relationship_user_icon_type_default: IconType = IconType.DEFAULT,
        relationship_user_glow_default: bool = DEFAULT_GLOW,
        relationship_user_account_id_default: int = DEFAULT_ID,
        relationship_user_message_state_default: MessageState = MessageState.DEFAULT,
    ) -> RU:
        mapping = split_relationship_user(string)

        return cls(
            name=mapping.get(relationship_user_name_index, relationship_user_name_default),
            id=parse_get_or(
                int, relationship_user_id_default, mapping.get(relationship_user_id_index)
            ),
            icon_id=parse_get_or(
                int, relationship_user_icon_id_default, mapping.get(relationship_user_icon_id_index)
            ),
            color_1_id=parse_get_or(
                int,
                relationship_user_color_1_id_default,
                mapping.get(relationship_user_color_1_id_index),
            ),
            color_2_id=parse_get_or(
                int,
                relationship_user_color_2_id_default,
                mapping.get(relationship_user_color_2_id_index),
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                relationship_user_icon_type_default,
                mapping.get(relationship_user_icon_type_index),
            ),
            glow=parse_get_or(
                int_bool, relationship_user_glow_default, mapping.get(relationship_user_glow_index)
            ),
            account_id=parse_get_or(
                int,
                relationship_user_account_id_default,
                mapping.get(relationship_user_account_id_index),
            ),
            message_state=parse_get_or(
                partial_parse_enum(int, MessageState),
                relationship_user_message_state_default,
                mapping.get(relationship_user_message_state_index),
            ),
        )

    def to_robtop(
        self,
        relationship_user_name_index: int = RELATIONSHIP_USER_NAME,
        relationship_user_id_index: int = RELATIONSHIP_USER_ID,
        relationship_user_icon_id_index: int = RELATIONSHIP_USER_ICON_ID,
        relationship_user_color_1_id_index: int = RELATIONSHIP_USER_COLOR_1_ID,
        relationship_user_color_2_id_index: int = RELATIONSHIP_USER_COLOR_2_ID,
        relationship_user_icon_type_index: int = RELATIONSHIP_USER_ICON_TYPE,
        relationship_user_glow_index: int = RELATIONSHIP_USER_GLOW,
        relationship_user_account_id_index: int = RELATIONSHIP_USER_ACCOUNT_ID,
        relationship_user_message_state_index: int = RELATIONSHIP_USER_MESSAGE_STATE,
    ) -> str:
        mapping = {
            relationship_user_name_index: str(self.name),
            relationship_user_id_index: str(self.id),
            relationship_user_icon_id_index: str(self.icon_id),
            relationship_user_color_1_id_index: str(self.color_1_id),
            relationship_user_color_2_id_index: str(self.color_2_id),
            relationship_user_icon_type_index: str(self.icon_type.value),
            relationship_user_glow_index: str(int(self.glow)),
            relationship_user_account_id_index: str(self.account_id),
            relationship_user_message_state_index: str(self.message_state.value),
        }

        return concat_relationship_user(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return RELATIONSHIP_USER_SEPARATOR in string


LEADERBOARD_USER_NAME = 1
LEADERBOARD_USER_ID = 2
LEADERBOARD_USER_STARS = 3
LEADERBOARD_USER_DEMONS = 4
LEADERBOARD_USER_PLACE = 6
LEADERBOARD_USER_CREATOR_POINTS = 8
LEADERBOARD_USER_ICON_ID = 9
LEADERBOARD_USER_COLOR_1_ID = 10
LEADERBOARD_USER_COLOR_2_ID = 11
LEADERBOARD_USER_SECRET_COINS = 13
LEADERBOARD_USER_ICON_TYPE = 14
LEADERBOARD_USER_GLOW = 15
LEADERBOARD_USER_ACCOUNT_ID = 16
LEADERBOARD_USER_USER_COINS = 17
LEADERBOARD_USER_DIAMONDS = 46

LU = TypeVar("LU", bound="LeaderboardUserModel")


@define()
class LeaderboardUserModel(Model):
    name: str = UNKNOWN
    id: int = DEFAULT_ID
    stars: int = DEFAULT_STARS
    demons: int = DEFAULT_DEMONS
    place: int = DEFAULT_PLACE
    creator_points: int = DEFAULT_CREATOR_POINTS
    icon_id: int = DEFAULT_ICON_ID
    color_1_id: int = DEFAULT_COLOR_1_ID
    color_2_id: int = DEFAULT_COLOR_2_ID
    secret_coins: int = DEFAULT_SECRET_COINS
    icon_type: IconType = IconType.DEFAULT
    glow: bool = DEFAULT_GLOW
    account_id: int = DEFAULT_ID
    user_coins: int = DEFAULT_USER_COINS
    diamonds: int = DEFAULT_DIAMONDS

    @classmethod
    def from_robtop(
        cls: Type[LU],
        string: str,
        # indexes
        leaderboard_user_name_index: int = LEADERBOARD_USER_NAME,
        leaderboard_user_id_index: int = LEADERBOARD_USER_ID,
        leaderboard_user_stars_index: int = LEADERBOARD_USER_STARS,
        leaderboard_user_demons_index: int = LEADERBOARD_USER_DEMONS,
        leaderboard_user_place_index: int = LEADERBOARD_USER_PLACE,
        leaderboard_user_creator_points_index: int = LEADERBOARD_USER_CREATOR_POINTS,
        leaderboard_user_icon_id_index: int = LEADERBOARD_USER_ICON_ID,
        leaderboard_user_color_1_id_index: int = LEADERBOARD_USER_COLOR_1_ID,
        leaderboard_user_color_2_id_index: int = LEADERBOARD_USER_COLOR_2_ID,
        leaderboard_user_secret_coins_index: int = LEADERBOARD_USER_SECRET_COINS,
        leaderboard_user_icon_type_index: int = LEADERBOARD_USER_ICON_TYPE,
        leaderboard_user_glow_index: int = LEADERBOARD_USER_GLOW,
        leaderboard_user_account_id_index: int = LEADERBOARD_USER_ACCOUNT_ID,
        leaderboard_user_user_coins_index: int = LEADERBOARD_USER_USER_COINS,
        leaderboard_user_diamonds_index: int = LEADERBOARD_USER_DIAMONDS,
        # defaults
        leaderboard_user_name_default: str = UNKNOWN,
        leaderboard_user_id_default: int = DEFAULT_ID,
        leaderboard_user_stars_default: int = DEFAULT_STARS,
        leaderboard_user_demons_default: int = DEFAULT_DEMONS,
        leaderboard_user_place_default: int = DEFAULT_PLACE,
        leaderboard_user_creator_points_default: int = DEFAULT_CREATOR_POINTS,
        leaderboard_user_icon_id_default: int = DEFAULT_ICON_ID,
        leaderboard_user_color_1_id_default: int = DEFAULT_COLOR_1_ID,
        leaderboard_user_color_2_id_default: int = DEFAULT_COLOR_2_ID,
        leaderboard_user_secret_coins_default: int = DEFAULT_SECRET_COINS,
        leaderboard_user_icon_type_default: IconType = IconType.DEFAULT,
        leaderboard_user_glow_default: bool = DEFAULT_GLOW,
        leaderboard_user_account_id_default: int = DEFAULT_ID,
        leaderboard_user_user_coins_default: int = DEFAULT_USER_COINS,
        leaderboard_user_diamonds_default: int = DEFAULT_DIAMONDS,
    ) -> LU:
        mapping = split_leaderboard_user(string)

        return cls(
            name=mapping.get(leaderboard_user_name_index, leaderboard_user_name_default),
            id=parse_get_or(
                int, leaderboard_user_id_default, mapping.get(leaderboard_user_id_index)
            ),
            stars=parse_get_or(
                int, leaderboard_user_stars_default, mapping.get(leaderboard_user_stars_index)
            ),
            demons=parse_get_or(
                int, leaderboard_user_demons_default, mapping.get(leaderboard_user_demons_index)
            ),
            place=parse_get_or(
                int, leaderboard_user_place_default, mapping.get(leaderboard_user_place_index)
            ),
            creator_points=parse_get_or(
                int,
                leaderboard_user_creator_points_default,
                mapping.get(leaderboard_user_creator_points_index),
            ),
            icon_id=parse_get_or(
                int, leaderboard_user_icon_id_default, mapping.get(leaderboard_user_icon_id_index)
            ),
            color_1_id=parse_get_or(
                int,
                leaderboard_user_color_1_id_default,
                mapping.get(leaderboard_user_color_1_id_index),
            ),
            color_2_id=parse_get_or(
                int,
                leaderboard_user_color_2_id_default,
                mapping.get(leaderboard_user_color_2_id_index),
            ),
            secret_coins=parse_get_or(
                int,
                leaderboard_user_secret_coins_default,
                mapping.get(leaderboard_user_secret_coins_index),
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                leaderboard_user_icon_type_default,
                mapping.get(leaderboard_user_icon_type_index),
            ),
            glow=parse_get_or(
                int_bool, leaderboard_user_glow_default, mapping.get(leaderboard_user_glow_index)
            ),
            account_id=parse_get_or(
                int,
                leaderboard_user_account_id_default,
                mapping.get(leaderboard_user_account_id_index),
            ),
            user_coins=parse_get_or(
                int,
                leaderboard_user_user_coins_default,
                mapping.get(leaderboard_user_user_coins_index),
            ),
            diamonds=parse_get_or(
                int, leaderboard_user_diamonds_default, mapping.get(leaderboard_user_diamonds_index)
            ),
        )

    def to_robtop(
        self,
        leaderboard_user_name_index: int = LEADERBOARD_USER_NAME,
        leaderboard_user_id_index: int = LEADERBOARD_USER_ID,
        leaderboard_user_stars_index: int = LEADERBOARD_USER_STARS,
        leaderboard_user_demons_index: int = LEADERBOARD_USER_DEMONS,
        leaderboard_user_place_index: int = LEADERBOARD_USER_PLACE,
        leaderboard_user_creator_points_index: int = LEADERBOARD_USER_CREATOR_POINTS,
        leaderboard_user_icon_id_index: int = LEADERBOARD_USER_ICON_ID,
        leaderboard_user_color_1_id_index: int = LEADERBOARD_USER_COLOR_1_ID,
        leaderboard_user_color_2_id_index: int = LEADERBOARD_USER_COLOR_2_ID,
        leaderboard_user_secret_coins_index: int = LEADERBOARD_USER_SECRET_COINS,
        leaderboard_user_icon_type_index: int = LEADERBOARD_USER_ICON_TYPE,
        leaderboard_user_glow_index: int = LEADERBOARD_USER_GLOW,
        leaderboard_user_account_id_index: int = LEADERBOARD_USER_ACCOUNT_ID,
        leaderboard_user_user_coins_index: int = LEADERBOARD_USER_USER_COINS,
        leaderboard_user_diamonds_index: int = LEADERBOARD_USER_DIAMONDS,
    ) -> str:
        glow = self.glow
        glow += glow

        mapping = {
            leaderboard_user_name_index: self.name,
            leaderboard_user_id_index: str(self.id),
            leaderboard_user_stars_index: str(self.stars),
            leaderboard_user_place_index: str(self.place),
            leaderboard_user_demons_index: str(self.demons),
            leaderboard_user_creator_points_index: str(self.creator_points),
            leaderboard_user_icon_id_index: str(self.icon_id),
            leaderboard_user_color_1_id_index: str(self.color_1_id),
            leaderboard_user_color_2_id_index: str(self.color_2_id),
            leaderboard_user_secret_coins_index: str(self.secret_coins),
            leaderboard_user_icon_type_index: str(self.icon_type.value),
            leaderboard_user_glow_index: str(glow),
            leaderboard_user_account_id_index: str(self.account_id),
            leaderboard_user_user_coins_index: str(self.user_coins),
            leaderboard_user_diamonds_index: str(self.diamonds),
        }

        return concat_leaderboard_user(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEADERBOARD_USER_SEPARATOR in string


TI = TypeVar("TI", bound="TimelyInfoModel")

TIMELY_ID_ADD = 100_000


@define()
class TimelyInfoModel(Model):
    id: int = field(default=DEFAULT_ID)
    type: TimelyType = field(default=TimelyType.DEFAULT)
    cooldown: timedelta = field(factory=timedelta)

    @classmethod
    def from_robtop(cls: Type[TI], string: str, type: TimelyType = TimelyType.DEFAULT) -> TI:
        timely_id, cooldown_seconds = map(int, split_timely_info(string))

        return cls(
            id=timely_id % TIMELY_ID_ADD, type=type, cooldown=timedelta(seconds=cooldown_seconds)
        )

    def to_robtop(self) -> str:
        timely_id = self.id

        if self.type.is_weekly():
            timely_id += TIMELY_ID_ADD

        cooldown = int(self.cooldown.total_seconds())

        values = (str(timely_id), str(cooldown))

        return concat_timely_info(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return TIMELY_INFO_SEPARATOR in string


MESSAGE_ID = 1
MESSAGE_ACCOUNT_ID = 2
MESSAGE_USER_ID = 3
MESSAGE_SUBJECT = 4
MESSAGE_CONTENT = 5
MESSAGE_NAME = 6
MESSAGE_CREATED_AT = 7
MESSAGE_READ = 8
MESSAGE_SENT = 9

M = TypeVar("M", bound="MessageModel")


@define()
class MessageModel(Model):
    id: int = field(default=DEFAULT_ID)
    account_id: int = field(default=DEFAULT_ID)
    user_id: int = field(default=DEFAULT_ID)
    subject: str = field(default=EMPTY)
    content: str = field(default=EMPTY)
    name: str = field(default=UNKNOWN)
    created_at: datetime = field(factory=datetime.utcnow)
    read: bool = field(default=DEFAULT_READ)
    sent: bool = field(default=DEFAULT_SENT)

    content_present: bool = field(default=DEFAULT_CONTENT_PRESENT)

    @classmethod
    def from_robtop(
        cls: Type[M],
        string: str,
        content_present: bool = DEFAULT_CONTENT_PRESENT,
        # indexes
        message_id_index: int = MESSAGE_ID,
        message_account_id_index: int = MESSAGE_ACCOUNT_ID,
        message_user_id_index: int = MESSAGE_USER_ID,
        message_subject_index: int = MESSAGE_SUBJECT,
        message_content_index: int = MESSAGE_CONTENT,
        message_name_index: int = MESSAGE_NAME,
        message_created_at_index: int = MESSAGE_CREATED_AT,
        message_read_index: int = MESSAGE_READ,
        message_sent_index: int = MESSAGE_SENT,
        # defaults
        message_id_default: int = DEFAULT_ID,
        message_account_id_default: int = DEFAULT_ID,
        message_user_id_default: int = DEFAULT_ID,
        message_subject_default: str = EMPTY,
        message_content_default: str = EMPTY,
        message_name_default: str = UNKNOWN,
        message_created_at_default: Optional[datetime] = None,
        message_read_default: bool = DEFAULT_READ,
        message_sent_default: bool = DEFAULT_SENT,
    ) -> M:
        if message_created_at_default is None:
            message_created_at_default = datetime.utcnow()

        mapping = split_message(string)

        message_created_at = mapping.get(message_created_at_index)

        if message_created_at is None:
            created_at = message_created_at_default

        else:
            created_at = datetime_from_human(message_created_at)

        return cls(
            id=parse_get_or(int, message_id_default, mapping.get(message_id_index)),
            account_id=parse_get_or(
                int, message_account_id_default, mapping.get(message_account_id_index)
            ),
            user_id=parse_get_or(
                int,
                message_user_id_default,
                mapping.get(message_user_id_index),
            ),
            subject=decode_base64_string_url_safe(
                mapping.get(message_subject_index, message_subject_default)
            ),
            content=decode_robtop_string(
                mapping.get(message_content_index, message_content_default), Key.MESSAGE
            ),
            name=mapping.get(message_name_index, message_name_default),
            created_at=created_at,
            read=parse_get_or(int_bool, message_read_default, mapping.get(message_read_index)),
            sent=parse_get_or(int_bool, message_sent_default, mapping.get(message_sent_index)),
            content_present=content_present,
        )

    def to_robtop(
        self,
        message_id_index: int = MESSAGE_ID,
        message_account_id_index: int = MESSAGE_ACCOUNT_ID,
        message_user_id_index: int = MESSAGE_USER_ID,
        message_subject_index: int = MESSAGE_SUBJECT,
        message_content_index: int = MESSAGE_CONTENT,
        message_name_index: int = MESSAGE_NAME,
        message_created_at_index: int = MESSAGE_CREATED_AT,
        message_read_index: int = MESSAGE_READ,
        message_sent_index: int = MESSAGE_SENT,
    ) -> str:
        mapping = {
            message_id_index: str(self.id),
            message_account_id_index: str(self.account_id),
            message_user_id_index: str(self.user_id),
            message_subject_index: encode_base64_string_url_safe(self.subject),
            message_content_index: encode_robtop_string(self.content, Key.MESSAGE),
            message_name_index: self.name,
            message_created_at_index: datetime_to_human(self.created_at),
            message_read_index: str(int(self.read)),
            message_sent_index: str(int(self.sent)),
        }

        return concat_message(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return MESSAGE_SEPARATOR in string

    def is_read(self) -> bool:
        return self.read

    def is_sent(self) -> bool:
        return self.sent

    def is_content_present(self) -> bool:
        return self.content_present


FRIEND_REQUEST_NAME = 1
FRIEND_REQUEST_USER_ID = 2
FRIEND_REQUEST_ICON_ID = 9
FRIEND_REQUEST_COLOR_1_ID = 10
FRIEND_REQUEST_COLOR_2_ID = 11
FRIEND_REQUEST_ICON_TYPE = 14
FRIEND_REQUEST_GLOW = 15
FRIEND_REQUEST_ACCOUNT_ID = 16
FRIEND_REQUEST_ID = 32
FRIEND_REQUEST_CONTENT = 35
FRIEND_REQUEST_CREATED_AT = 37
FRIEND_REQUEST_UNREAD = 41


class FriendRequestModel(Model):
    name: str = field(default=UNKNOWN)
    user_id: int = field(default=DEFAULT_ID)
    icon_id: int = field(default=DEFAULT_ICON_ID)
    color_1_id: int = field(default=DEFAULT_COLOR_1_ID)
    color_2_id: int = field(default=DEFAULT_COLOR_2_ID)
    icon_type: IconType = field(default=IconType.DEFAULT)
    glow: bool = field(default=DEFAULT_GLOW)
    account_id: int = field(default=DEFAULT_ID)
    id: int = field(default=DEFAULT_ID)
    content: str = field(default=EMPTY)
    created_at: datetime = field(default=datetime.utcnow)
    unread: bool = field(default=DEFAULT_UNREAD)


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


RR = TypeVar("RR", bound="RelationshipsResponseModel")


@define()
class RelationshipsResponseModel(Model):
    users: List[RelationshipUserModel] = field(factory=list)

    @classmethod
    def from_robtop(cls: Type[RR], string: str) -> RR:
        users = [
            RelationshipUserModel.from_robtop(string)
            for string in split_relationships_response_users(string)
        ]

        return cls(users=users)

    def to_robtop(self) -> str:
        return concat_relationships_response_users(user.to_robtop() for user in self.users)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return RELATIONSHIPS_RESPONSE_USERS_SEPARATOR in string


LR = TypeVar("LR", bound="LeaderboardResponseModel")


@define()
class LeaderboardResponseModel(Model):
    users: List[LeaderboardUserModel] = field(factory=list)

    @classmethod
    def from_robtop(cls: Type[LR], string: str) -> LR:
        users = [
            LeaderboardUserModel.from_robtop(string)
            for string in split_leaderboard_response_users(string)
        ]

        return cls(users=users)

    def to_robtop(self) -> str:
        return concat_leaderboard_response_users(user.to_robtop() for user in self.users)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEADERBOARD_RESPONSE_USERS_SEPARATOR in string


MR = TypeVar("MR", bound="MessagesResponseModel")


@define()
class MessagesResponseModel(Model):
    messages: List[MessageModel] = field(factory=list)
    pages: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[MR], string: str) -> MR:
        messages_string, pages_string = split_messages_response(string)

        messages = [
            MessageModel.from_robtop(string, content_present=False)
            for string in split_messages_response_messages(messages_string)
        ]

        pages = PageModel.from_robtop(pages_string)

        return cls(messages=messages, pages=pages)

    def to_robtop(self) -> str:
        values = (
            concat_messages_response_messages(message.to_robtop() for message in self.messages),
            self.pages.to_robtop(),
        )

        return concat_messages_response(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return MESSAGES_RESPONSE_SEPARATOR in string


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
