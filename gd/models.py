from datetime import datetime, timedelta
from typing import Iterator, List, Optional, Type, TypeVar
from urllib.parse import quote, unquote

from attrs import define, field
from typing_extensions import Protocol
from yarl import URL

from gd.constants import (
    DEFAULT_ACTIVE,
    DEFAULT_AUTO,
    DEFAULT_COINS,
    DEFAULT_COLOR_1_ID,
    DEFAULT_COLOR_2_ID,
    DEFAULT_CONTENT_PRESENT,
    DEFAULT_CREATOR_POINTS,
    DEFAULT_DEMON,
    DEFAULT_DEMONS,
    DEFAULT_DENOMINATOR,
    DEFAULT_DIAMONDS,
    DEFAULT_DOWNLOADS,
    DEFAULT_EPIC,
    DEFAULT_GLOW,
    DEFAULT_ICON_ID,
    DEFAULT_ID,
    DEFAULT_LOW_DETAIL,
    DEFAULT_NEW,
    DEFAULT_NUMERATOR,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_PLACE,
    DEFAULT_RANK,
    DEFAULT_RATING,
    DEFAULT_READ,
    DEFAULT_SCORE,
    DEFAULT_SECRET_COINS,
    DEFAULT_SENT,
    DEFAULT_SIZE,
    DEFAULT_STARS,
    DEFAULT_TWO_PLAYER,
    DEFAULT_UNREAD,
    DEFAULT_USER_COINS,
    DEFAULT_VERIFIED_COINS,
    DEFAULT_VERSION,
    EMPTY,
    TIMELY_ID_ADD,
    UNKNOWN,
    UNNAMED,
)
from gd.datetime import datetime_from_human, datetime_to_human
from gd.encoding import (
    decode_base64_string_url_safe,
    decode_robtop_string,
    encode_base64_string_url_safe,
    encode_robtop_string,
    generate_level_seed,
    sha1_string_with_salt,
)
from gd.enums import (
    CommentState,
    DemonDifficulty,
    Difficulty,
    FriendRequestState,
    FriendState,
    IconType,
    Key,
    LevelDifficulty,
    LevelLength,
    MessageState,
    Role,
    Salt,
    TimelyType,
)
from gd.models_constants import (
    COMMENT_BANNED_SEPARATOR,
    CREATOR_SEPARATOR,
    DATABASE_SEPARATOR,
    FRIEND_REQUEST_SEPARATOR,
    LEADERBOARD_RESPONSE_USERS_SEPARATOR,
    LEADERBOARD_USER_SEPARATOR,
    LEVEL_RESPONSE_SEPARATOR,
    LEVEL_SEPARATOR,
    LOGIN_SEPARATOR,
    MESSAGE_SEPARATOR,
    MESSAGES_RESPONSE_SEPARATOR,
    PAGE_SEPARATOR,
    PROFILE_SEPARATOR,
    RELATIONSHIP_USER_SEPARATOR,
    RELATIONSHIPS_RESPONSE_USERS_SEPARATOR,
    SEARCH_LEVELS_RESPONSE_SEPARATOR,
    SEARCH_USER_SEPARATOR,
    SEARCH_USERS_RESPONSE_SEPARATOR,
    SONG_SEPARATOR,
    TIMELY_INFO_SEPARATOR,
)
from gd.models_utils import (
    concat_comment_banned,
    concat_creator,
    concat_friend_request,
    concat_friend_requests_response,
    concat_friend_requests_response_friend_requests,
    concat_leaderboard_response_users,
    concat_leaderboard_user,
    concat_level,
    concat_level_response,
    concat_login,
    concat_message,
    concat_messages_response,
    concat_messages_response_messages,
    concat_page,
    concat_profile,
    concat_relationship_user,
    concat_relationships_response_users,
    concat_search_levels_response,
    concat_search_levels_response_creators,
    concat_search_levels_response_levels,
    concat_search_levels_response_songs,
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
    split_friend_request,
    split_friend_requests_response,
    split_friend_requests_response_friend_requests,
    split_leaderboard_response_users,
    split_leaderboard_user,
    split_level,
    split_level_response,
    split_login,
    split_message,
    split_messages_response,
    split_messages_response_messages,
    split_page,
    split_profile,
    split_relationship_user,
    split_relationships_response_users,
    split_search_levels_response,
    split_search_levels_response_creators,
    split_search_levels_response_levels,
    split_search_levels_response_songs,
    split_search_user,
    split_search_users_response,
    split_search_users_response_users,
    split_song,
    split_timely_info,
)
from gd.password import Password
from gd.robtop import RobTop
from gd.string_utils import concat_empty
from gd.versions import GameVersion, CURRENT_GAME_VERSION

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


LG = TypeVar("LG", bound="LoginModel")


@define()
class LoginModel(Model):
    account_id: int = 0
    id: int = 0

    @classmethod
    def from_robtop(cls: Type[LG], string: str) -> LG:
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
    id: int = DEFAULT_ID
    name: str = UNKNOWN
    account_id: int = DEFAULT_ID

    @classmethod
    def from_robtop(cls: Type[C], string: str) -> C:
        id_string, name, account_id_string = split_creator(string)

        return cls(int(id_string), name, int(account_id_string))

    def to_robtop(self) -> str:
        values = (str(self.id), self.name, str(self.account_id))

        return concat_creator(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return CREATOR_SEPARATOR in string


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
        total_string, start_string, stop_string = split_page(string)

        if not total_string:
            total = None

        else:
            total = int(total_string)

        start = int(start_string)
        stop = int(stop_string)

        return cls(total, start, stop)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return PAGE_SEPARATOR in string

    def to_robtop(self) -> str:
        total = self.total
        start = self.start
        stop = self.stop

        if total is None:
            values = (EMPTY, str(start), str(stop))

        else:
            values = (str(total), str(start), str(stop))

        return concat_page(values)


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
            created_at=parse_get_or(
                datetime_from_human,
                message_created_at_default,
                mapping.get(message_created_at_index),
                ignore_errors=True,
            ),
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

FR = TypeVar("FR", bound="FriendRequestModel")


@define()
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
    created_at: datetime = field(factory=datetime.utcnow)
    unread: bool = field(default=DEFAULT_UNREAD)

    @classmethod
    def from_robtop(
        cls: Type[FR],
        string: str,
        # indexes
        friend_request_name_index: int = FRIEND_REQUEST_NAME,
        friend_request_user_id_index: int = FRIEND_REQUEST_USER_ID,
        friend_request_icon_id_index: int = FRIEND_REQUEST_ICON_ID,
        friend_request_color_1_id_index: int = FRIEND_REQUEST_COLOR_1_ID,
        friend_request_color_2_id_index: int = FRIEND_REQUEST_COLOR_2_ID,
        friend_request_icon_type_index: int = FRIEND_REQUEST_ICON_TYPE,
        friend_request_glow_index: int = FRIEND_REQUEST_GLOW,
        friend_request_account_id_index: int = FRIEND_REQUEST_ACCOUNT_ID,
        friend_request_id_index: int = FRIEND_REQUEST_ID,
        friend_request_content_index: int = FRIEND_REQUEST_CONTENT,
        friend_request_created_at_index: int = FRIEND_REQUEST_CREATED_AT,
        friend_request_unread_index: int = FRIEND_REQUEST_UNREAD,
        # defaults
        friend_request_name_default: str = UNKNOWN,
        friend_request_user_id_default: int = DEFAULT_ID,
        friend_request_icon_id_default: int = DEFAULT_ICON_ID,
        friend_request_color_1_id_default: int = DEFAULT_COLOR_1_ID,
        friend_request_color_2_id_default: int = DEFAULT_COLOR_2_ID,
        friend_request_icon_type_default: IconType = IconType.DEFAULT,
        friend_request_glow_default: bool = DEFAULT_GLOW,
        friend_request_account_id_default: int = DEFAULT_ID,
        friend_request_id_default: int = DEFAULT_ID,
        friend_request_content_default: str = EMPTY,
        friend_request_created_at_default: Optional[datetime] = None,
        friend_request_unread_default: bool = DEFAULT_UNREAD,
    ) -> FR:
        if friend_request_created_at_default is None:
            friend_request_created_at_default = datetime.utcnow()

        mapping = split_friend_request(string)

        return cls(
            name=mapping.get(friend_request_name_index, friend_request_name_default),
            user_id=parse_get_or(
                int, friend_request_user_id_default, mapping.get(friend_request_user_id_index)
            ),
            icon_id=parse_get_or(
                int, friend_request_icon_id_default, mapping.get(friend_request_icon_id_index)
            ),
            color_1_id=parse_get_or(
                int,
                friend_request_color_1_id_default,
                mapping.get(friend_request_color_1_id_index),
            ),
            color_2_id=parse_get_or(
                int,
                friend_request_color_2_id_default,
                mapping.get(friend_request_color_2_id_index),
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                friend_request_icon_type_default,
                mapping.get(friend_request_icon_type_index),
            ),
            glow=parse_get_or(
                int_bool, friend_request_glow_default, mapping.get(friend_request_glow_index)
            ),
            account_id=parse_get_or(
                int, friend_request_account_id_default, mapping.get(friend_request_account_id_index)
            ),
            id=parse_get_or(
                int, friend_request_id_default, mapping.get(friend_request_id_index)
            ),
            content=decode_base64_string_url_safe(
                mapping.get(friend_request_content_index, friend_request_content_default)
            ),
            created_at=parse_get_or(
                datetime_from_human,
                friend_request_created_at_default,
                mapping.get(friend_request_created_at_index),
                ignore_errors=True,
            ),
            unread=parse_get_or(
                int_bool, friend_request_unread_default, mapping.get(friend_request_unread_index)
            ),
        )

    def to_robtop(
        self,
        friend_request_name_index: int = FRIEND_REQUEST_NAME,
        friend_request_user_id_index: int = FRIEND_REQUEST_USER_ID,
        friend_request_icon_id_index: int = FRIEND_REQUEST_ICON_ID,
        friend_request_color_1_id_index: int = FRIEND_REQUEST_COLOR_1_ID,
        friend_request_color_2_id_index: int = FRIEND_REQUEST_COLOR_2_ID,
        friend_request_icon_type_index: int = FRIEND_REQUEST_ICON_TYPE,
        friend_request_glow_index: int = FRIEND_REQUEST_GLOW,
        friend_request_account_id_index: int = FRIEND_REQUEST_ACCOUNT_ID,
        friend_request_id_index: int = FRIEND_REQUEST_ID,
        friend_request_content_index: int = FRIEND_REQUEST_CONTENT,
        friend_request_created_at_index: int = FRIEND_REQUEST_CREATED_AT,
        friend_request_unread_index: int = FRIEND_REQUEST_UNREAD,
    ) -> str:
        glow = self.glow

        glow += glow

        unread = EMPTY if self.is_read() else str(int(self.unread))

        mapping = {
            friend_request_name_index: self.name,
            friend_request_user_id_index: str(self.user_id),
            friend_request_icon_id_index: str(self.icon_id),
            friend_request_color_1_id_index: str(self.color_1_id),
            friend_request_color_2_id_index: str(self.color_2_id),
            friend_request_icon_type_index: str(self.icon_type.value),
            friend_request_glow_index: str(glow),
            friend_request_account_id_index: str(self.account_id),
            friend_request_id_index: str(self.id),
            friend_request_content_index: encode_base64_string_url_safe(self.content),
            friend_request_created_at_index: datetime_to_human(self.created_at),
            friend_request_unread_index: unread,
        }

        return concat_friend_request(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return FRIEND_REQUEST_SEPARATOR in string

    def is_unread(self) -> bool:
        return self.unread

    def is_read(self) -> bool:
        return self.read

    @property
    def read(self) -> bool:
        return not self.unread

    @read.setter
    def read(self, read: bool) -> None:
        self.unread = not read


LEVEL_ID = 1
LEVEL_NAME = 2
LEVEL_DESCRIPTION = 3
LEVEL_UNPROCESSED_DATA = 4
LEVEL_VERSION = 5
LEVEL_CREATOR_ID = 6
LEVEL_DIFFICULTY_NUMERATOR = 8
LEVEL_DIFFICULTY_DENOMINATOR = 9
LEVEL_DOWNLOADS = 10
LEVEL_OFFICIAL_SONG_ID = 12
LEVEL_GAME_VERSION = 13
LEVEL_RATING = 14
LEVEL_LENGTH = 15
LEVEL_DEMON = 17
LEVEL_STARS = 18
LEVEL_SCORE = 19
LEVEL_AUTO = 25
LEVEL_PASSWORD_DATA = 27
LEVEL_UPLOADED_AT = 28
LEVEL_UPDATED_AT = 29
LEVEL_ORIGINAL_ID = 30
LEVEL_TWO_PLAYER = 31
LEVEL_CUSTOM_SONG_ID = 35
LEVEL_EXTRA_STRING = 36
LEVEL_COINS = 37
LEVEL_VERIFIED_COINS = 38
LEVEL_REQUESTED_STARS = 39
LEVEL_LOW_DETAIL = 40
LEVEL_TIMELY_ID = 41
LEVEL_EPIC = 42
LEVEL_DEMON_DIFFICULTY = 43
LEVEL_OBJECT_COUNT = 45
LEVEL_EDITOR_TIME = 46
LEVEL_COPIES_TIME = 47


L = TypeVar("L", bound="LevelModel")


VALUE_TO_DEMON_DIFFICULTY = {
    3: DemonDifficulty.EASY_DEMON,
    4: DemonDifficulty.MEDIUM_DEMON,
    5: DemonDifficulty.INSANE_DEMON,
    6: DemonDifficulty.EXTREME_DEMON,
}

DEMON_DIFFICULTY_TO_VALUE = {
    demon_difficulty: value for value, demon_difficulty in VALUE_TO_DEMON_DIFFICULTY.items()
}


@define()
class LevelModel(Model):
    id: int = DEFAULT_ID
    name: str = UNNAMED
    description: str = EMPTY
    unprocessed_data: str = EMPTY
    version: int = DEFAULT_VERSION
    creator_id: int = DEFAULT_ID
    difficulty_denominator: int = DEFAULT_DENOMINATOR
    difficulty_numerator: int = DEFAULT_NUMERATOR
    downloads: int = DEFAULT_DOWNLOADS
    official_song_id: int = DEFAULT_ID
    game_version: GameVersion = CURRENT_GAME_VERSION
    rating: int = DEFAULT_RATING
    length: LevelLength = LevelLength.DEFAULT
    demon: bool = DEFAULT_DEMON
    stars: int = DEFAULT_STARS
    score: int = DEFAULT_SCORE
    auto: bool = DEFAULT_AUTO
    password_data: Password = field(factory=Password)
    uploaded_at: datetime = field(factory=datetime.utcnow)
    updated_at: datetime = field(factory=datetime.utcnow)
    original_id: int = DEFAULT_ID
    two_player: bool = DEFAULT_TWO_PLAYER
    custom_song_id: int = DEFAULT_ID
    extra_string: str = EMPTY
    coins: int = DEFAULT_COINS
    verified_coins: bool = DEFAULT_VERIFIED_COINS
    requested_stars: int = DEFAULT_STARS
    low_detail: bool = DEFAULT_LOW_DETAIL
    timely_id: int = DEFAULT_ID
    timely_type: TimelyType = TimelyType.DEFAULT
    epic: bool = DEFAULT_EPIC
    demon_difficulty: DemonDifficulty = DemonDifficulty.DEFAULT
    object_count: int = DEFAULT_OBJECT_COUNT
    editor_time: timedelta = field(factory=timedelta)
    copies_time: timedelta = field(factory=timedelta)

    @classmethod
    def from_robtop(
        cls: Type[L],
        string: str,
        # indexes
        level_id_index: int = LEVEL_ID,
        level_name_index: int = LEVEL_NAME,
        level_description_index: int = LEVEL_DESCRIPTION,
        level_unprocessed_data_index: int = LEVEL_UNPROCESSED_DATA,
        level_version_index: int = LEVEL_VERSION,
        level_creator_id_index: int = LEVEL_CREATOR_ID,
        level_difficulty_numerator_index: int = LEVEL_DIFFICULTY_NUMERATOR,
        level_difficulty_denominator_index: int = LEVEL_DIFFICULTY_DENOMINATOR,
        level_downloads_index: int = LEVEL_DOWNLOADS,
        level_official_song_id_index: int = LEVEL_OFFICIAL_SONG_ID,
        level_game_version_index: int = LEVEL_GAME_VERSION,
        level_rating_index: int = LEVEL_RATING,
        level_length_index: int = LEVEL_LENGTH,
        level_demon_index: int = LEVEL_DEMON,
        level_stars_index: int = LEVEL_STARS,
        level_score_index: int = LEVEL_SCORE,
        level_auto_index: int = LEVEL_AUTO,
        level_password_data_index: int = LEVEL_PASSWORD_DATA,
        level_uploaded_at_index: int = LEVEL_UPLOADED_AT,
        level_updated_at_index: int = LEVEL_UPDATED_AT,
        level_original_id_index: int = LEVEL_ORIGINAL_ID,
        level_two_player_index: int = LEVEL_TWO_PLAYER,
        level_custom_song_id_index: int = LEVEL_CUSTOM_SONG_ID,
        level_extra_string_index: int = LEVEL_EXTRA_STRING,
        level_coins_index: int = LEVEL_COINS,
        level_verified_coins_index: int = LEVEL_VERIFIED_COINS,
        level_requested_stars_index: int = LEVEL_REQUESTED_STARS,
        level_low_detail_index: int = LEVEL_LOW_DETAIL,
        level_timely_id_index: int = LEVEL_TIMELY_ID,
        level_epic_index: int = LEVEL_EPIC,
        level_demon_difficulty_index: int = LEVEL_DEMON_DIFFICULTY,
        level_object_count_index: int = LEVEL_OBJECT_COUNT,
        level_editor_time_index: int = LEVEL_EDITOR_TIME,
        level_copies_time_index: int = LEVEL_COPIES_TIME,
        # defaults
        level_id_default: int = DEFAULT_ID,
        level_name_default: str = UNNAMED,
        level_description_default: str = EMPTY,
        level_unprocessed_data_default: str = EMPTY,
        level_version_default: int = DEFAULT_VERSION,
        level_creator_id_default: int = DEFAULT_ID,
        level_difficulty_denominator_default: int = DEFAULT_DENOMINATOR,
        level_difficulty_numerator_default: int = DEFAULT_NUMERATOR,
        level_downloads_default: int = DEFAULT_DOWNLOADS,
        level_official_song_id_default: int = DEFAULT_ID,
        level_game_version_default: GameVersion = CURRENT_GAME_VERSION,
        level_rating_default: int = DEFAULT_RATING,
        level_length_default: LevelLength = LevelLength.DEFAULT,
        level_demon_default: bool = DEFAULT_DEMON,
        level_stars_default: int = DEFAULT_STARS,
        level_score_default: int = DEFAULT_SCORE,
        level_auto_default: bool = DEFAULT_AUTO,
        level_password_data_default: Optional[Password] = None,
        level_uploaded_at_default: Optional[datetime] = None,
        level_updated_at_default: Optional[datetime] = None,
        level_original_id_default: int = DEFAULT_ID,
        level_two_player_default: bool = DEFAULT_TWO_PLAYER,
        level_custom_song_id_default: int = DEFAULT_ID,
        level_extra_string_default: str = EMPTY,
        level_coins_default: int = DEFAULT_COINS,
        level_verified_coins_default: bool = DEFAULT_VERIFIED_COINS,
        level_requested_stars_default: int = DEFAULT_STARS,
        level_low_detail_default: bool = DEFAULT_LOW_DETAIL,
        level_timely_id_default: int = DEFAULT_ID,
        level_epic_default: bool = DEFAULT_EPIC,
        level_demon_difficulty_default: DemonDifficulty = DemonDifficulty.DEFAULT,
        level_object_count_default: int = DEFAULT_OBJECT_COUNT,
        level_editor_time_default: Optional[timedelta] = None,
        level_copies_time_default: Optional[timedelta] = None,
    ) -> L:
        if level_password_data_default is None:
            level_password_data_default = Password()

        if level_uploaded_at_default is None:
            level_uploaded_at_default = datetime.utcnow()

        if level_updated_at_default is None:
            level_updated_at_default = datetime.utcnow()

        if level_editor_time_default is None:
            level_editor_time_default = timedelta()

        if level_copies_time_default is None:
            level_copies_time_default = timedelta()

        mapping = split_level(string)

        level_demon_difficulty = mapping.get(level_demon_difficulty_index)

        if level_demon_difficulty is None:
            demon_difficulty = level_demon_difficulty_default

        else:
            demon_difficulty_value = int(level_demon_difficulty)

            demon_difficulty = VALUE_TO_DEMON_DIFFICULTY.get(demon_difficulty_value, DemonDifficulty.HARD_DEMON)

        level_editor_time = mapping.get(level_editor_time_index)

        if level_editor_time:
            editor_time = timedelta(seconds=int(level_editor_time))

        else:
            editor_time = level_editor_time_default

        level_copies_time = mapping.get(level_copies_time_index)

        if level_copies_time:
            copies_time = timedelta(seconds=int(level_copies_time))

        else:
            copies_time = level_copies_time_default

        timely_id = parse_get_or(
            int, level_timely_id_default, mapping.get(level_timely_id_index)
        )

        if timely_id:
            if timely_id // TIMELY_ID_ADD:
                timely_type = TimelyType.WEEKLY

            else:
                timely_type = TimelyType.DAILY

        else:
            timely_type = TimelyType.NOT_TIMELY

        timely_id %= TIMELY_ID_ADD

        return cls(
            id=parse_get_or(int, level_id_default, mapping.get(level_id_index)),
            name=mapping.get(level_name_index, level_name_default),
            description=decode_base64_string_url_safe(
                mapping.get(level_description_index, level_description_default)
            ),
            unprocessed_data=mapping.get(
                level_unprocessed_data_index, level_unprocessed_data_default
            ),
            version=parse_get_or(int, level_version_default, mapping.get(level_version_index)),
            creator_id=parse_get_or(
                int, level_creator_id_default, mapping.get(level_creator_id_index)
            ),
            difficulty_denominator=parse_get_or(
                int,
                level_difficulty_denominator_default,
                mapping.get(level_difficulty_denominator_index),
            ),
            difficulty_numerator=parse_get_or(
                int,
                level_difficulty_numerator_default,
                mapping.get(level_difficulty_numerator_index),
            ),
            downloads=parse_get_or(
                int, level_downloads_default, mapping.get(level_downloads_index)
            ),
            official_song_id=parse_get_or(
                int,
                level_official_song_id_default,
                mapping.get(level_official_song_id_index),
            ),
            game_version=parse_get_or(
                GameVersion.from_robtop,
                level_game_version_default,
                mapping.get(level_game_version_index),
            ),
            rating=parse_get_or(int, level_rating_default, mapping.get(level_rating_index)),
            length=parse_get_or(
                partial_parse_enum(int, LevelLength),
                level_length_default,
                mapping.get(level_length_index),
            ),
            demon=parse_get_or(int_bool, level_demon_default, mapping.get(level_demon_index)),
            stars=parse_get_or(int, level_stars_default, mapping.get(level_stars_index)),
            score=parse_get_or(int, level_score_default, mapping.get(level_score_index)),
            auto=parse_get_or(int_bool, level_auto_default, mapping.get(level_auto_index)),
            password_data=parse_get_or(
                Password.from_robtop,
                level_password_data_default,
                mapping.get(level_password_data_index),
            ),
            uploaded_at=parse_get_or(
                datetime_from_human,
                level_uploaded_at_default,
                mapping.get(level_uploaded_at_index),
                ignore_errors=True,
            ),
            updated_at=parse_get_or(
                datetime_from_human,
                level_updated_at_default,
                mapping.get(level_updated_at_index),
                ignore_errors=True,
            ),
            original_id=parse_get_or(
                int, level_original_id_default, mapping.get(level_original_id_index)
            ),
            two_player=parse_get_or(
                int_bool, level_two_player_default, mapping.get(level_two_player_index)
            ),
            custom_song_id=parse_get_or(
                int, level_custom_song_id_default, mapping.get(level_custom_song_id_index)
            ),
            extra_string=mapping.get(level_extra_string_index, level_extra_string_default),
            coins=parse_get_or(int, level_coins_default, mapping.get(level_coins_index)),
            verified_coins=parse_get_or(
                int_bool, level_verified_coins_default, mapping.get(level_verified_coins_index)
            ),
            requested_stars=parse_get_or(
                int, level_requested_stars_default, mapping.get(level_requested_stars_index)
            ),
            low_detail=parse_get_or(
                int_bool, level_low_detail_default, mapping.get(level_low_detail_index)
            ),
            timely_id=timely_id,
            timely_type=timely_type,
            epic=parse_get_or(int_bool, level_epic_default, mapping.get(level_epic_index)),
            demon_difficulty=demon_difficulty,
            object_count=parse_get_or(
                int, level_object_count_default, mapping.get(level_object_count_index)
            ),
            editor_time=editor_time,
            copies_time=copies_time,
        )

    def to_robtop(
        self,
        level_id_index: int = LEVEL_ID,
        level_name_index: int = LEVEL_NAME,
        level_description_index: int = LEVEL_DESCRIPTION,
        level_unprocessed_data_index: int = LEVEL_UNPROCESSED_DATA,
        level_version_index: int = LEVEL_VERSION,
        level_creator_id_index: int = LEVEL_CREATOR_ID,
        level_difficulty_numerator_index: int = LEVEL_DIFFICULTY_NUMERATOR,
        level_difficulty_denominator_index: int = LEVEL_DIFFICULTY_DENOMINATOR,
        level_downloads_index: int = LEVEL_DOWNLOADS,
        level_official_song_id_index: int = LEVEL_OFFICIAL_SONG_ID,
        level_game_version_index: int = LEVEL_GAME_VERSION,
        level_rating_index: int = LEVEL_RATING,
        level_length_index: int = LEVEL_LENGTH,
        level_demon_index: int = LEVEL_DEMON,
        level_stars_index: int = LEVEL_STARS,
        level_score_index: int = LEVEL_SCORE,
        level_auto_index: int = LEVEL_AUTO,
        level_password_data_index: int = LEVEL_PASSWORD_DATA,
        level_uploaded_at_index: int = LEVEL_UPLOADED_AT,
        level_updated_at_index: int = LEVEL_UPDATED_AT,
        level_original_id_index: int = LEVEL_ORIGINAL_ID,
        level_two_player_index: int = LEVEL_TWO_PLAYER,
        level_custom_song_id_index: int = LEVEL_CUSTOM_SONG_ID,
        level_extra_string_index: int = LEVEL_EXTRA_STRING,
        level_coins_index: int = LEVEL_COINS,
        level_verified_coins_index: int = LEVEL_VERIFIED_COINS,
        level_requested_stars_index: int = LEVEL_REQUESTED_STARS,
        level_low_detail_index: int = LEVEL_LOW_DETAIL,
        level_timely_id_index: int = LEVEL_TIMELY_ID,
        level_epic_index: int = LEVEL_EPIC,
        level_demon_difficulty_index: int = LEVEL_DEMON_DIFFICULTY,
        level_object_count_index: int = LEVEL_OBJECT_COUNT,
        level_editor_time_index: int = LEVEL_EDITOR_TIME,
        level_copies_time_index: int = LEVEL_COPIES_TIME,
    ) -> str:
        timely_id = self.timely_id

        if self.timely_type.is_weekly():
            timely_id += TIMELY_ID_ADD

        demon_difficulty_value = DEMON_DIFFICULTY_TO_VALUE.get(self.demon_difficulty, DemonDifficulty.DEMON.value)

        mapping = {
            level_id_index: str(self.id),
            level_name_index: self.name,
            level_description_index: encode_base64_string_url_safe(self.description),
            level_unprocessed_data_index: self.unprocessed_data,
            level_version_index: str(self.version),
            level_creator_id_index: str(self.creator_id),
            level_difficulty_denominator_index: str(self.difficulty_denominator),
            level_difficulty_numerator_index: str(self.difficulty_numerator),
            level_downloads_index: str(self.downloads),
            level_official_song_id_index: str(self.official_song_id),
            level_game_version_index: self.game_version.to_robtop(),
            level_rating_index: str(self.rating),
            level_length_index: str(self.length.value),
            level_demon_index: str(int(self.demon)) if self.is_demon() else EMPTY,
            level_stars_index: str(self.stars),
            level_score_index: str(self.score),
            level_auto_index: str(int(self.auto)) if self.is_auto() else EMPTY,
            level_password_data_index: self.password_data.to_robtop(),
            level_uploaded_at_index: datetime_to_human(self.uploaded_at),
            level_updated_at_index: datetime_to_human(self.updated_at),
            level_original_id_index: str(self.original_id),
            level_two_player_index: str(int(self.two_player)) if self.is_two_player() else EMPTY,
            level_custom_song_id_index: str(self.custom_song_id),
            level_extra_string_index: self.extra_string,
            level_coins_index: str(self.coins),
            level_verified_coins_index: str(int(self.verified_coins)),
            level_requested_stars_index: str(self.requested_stars),
            level_low_detail_index: str(int(self.low_detail)),
            level_timely_id_index: str(timely_id),
            level_epic_index: str(int(self.epic)),
            level_demon_difficulty_index: str(demon_difficulty_value),
            level_object_count_index: str(self.object_count),
            level_editor_time_index: str(int(self.editor_time.total_seconds())),
            level_copies_time_index: str(int(self.copies_time.total_seconds())),
        }

        return concat_level(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_SEPARATOR in string

    def is_demon(self) -> bool:
        return self.demon

    def is_auto(self) -> bool:
        return self.auto

    def is_two_player(self) -> bool:
        return self.two_player

    def has_low_detail(self) -> bool:
        return self.low_detail

    def is_epic(self) -> bool:
        return self.epic

    @property
    def difficulty(self) -> Difficulty:
        if self.is_auto():
            return Difficulty.AUTO

        if self.is_demon():
            return self.demon_difficulty.into_difficulty()

        return self.level_difficulty.into_difficulty()

    @property
    def level_difficulty(self) -> LevelDifficulty:
        difficulty_numerator = self.difficulty_numerator
        difficulty_denominator = self.difficulty_denominator

        if difficulty_denominator:
            difficulty_value = difficulty_numerator // difficulty_denominator

            if difficulty_value:
                return LevelDifficulty(difficulty_value)

        return LevelDifficulty.DEFAULT


LR = TypeVar("LR", bound="LevelResponseModel")

SMART_HASH_COUNT = 40


@define()
class LevelResponseModel:
    level: LevelModel = field(factory=LevelModel)
    smart_hash: str = field()  # *smart* hash
    hash: str = field()
    creator: Optional[CreatorModel] = field(default=None)

    @smart_hash.default
    def default_smart_hash(self) -> str:
        return sha1_string_with_salt(generate_level_seed(self.level.to_robtop(), SMART_HASH_COUNT), Salt.LEVEL)

    @hash.default
    def default_hash(self) -> str:
        return sha1_string_with_salt(self.level.to_robtop(), Salt.LEVEL)

    @classmethod
    def from_robtop(cls: Type[LR], string: str) -> LR:
        try:
            level_string, smart_hash, hash = split_level_response(string)

            creator = None

        except ValueError:
            level_string, smart_hash, hash, creator_string = split_level_response(string)

            creator = CreatorModel.from_robtop(creator_string)

        level = LevelModel.from_robtop(level_string)

        return cls(level=level, smart_hash=smart_hash, hash=hash, creator=creator)

    def to_robtop(self) -> str:
        values = (self.level.to_robtop(), self.hash)

        return concat_level_response(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_RESPONSE_SEPARATOR in string


SLR = TypeVar("SLR", bound="SearchLevelsResponseModel")

FIRST = 0
LAST = ~0


@define()
class SearchLevelsResponseModel(Model):
    levels: List[LevelModel] = field(factory=list)
    creators: List[CreatorModel] = field(factory=list)
    songs: List[SongModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)
    hash: str = field()

    def default_hash_iterator(self) -> Iterator[str]:
        first = FIRST
        last = LAST

        for level in self.levels:
            string = str(level.id)

            values = (string[first], string[last], str(level.stars), str(level.coins))

            yield concat_empty(values)

    @hash.default
    def default_hash(self) -> str:
        return sha1_string_with_salt(concat_empty(self.default_hash_iterator()), Salt.LEVEL)

    @classmethod
    def from_robtop(cls: Type[SLR], string: str) -> SLR:
        levels_string, creators_string, songs_string, page_string, hash = split_search_levels_response(string)

        levels = [
            LevelModel.from_robtop(string) for string
            in split_search_levels_response_levels(levels_string)
        ]

        creators = [
            CreatorModel.from_robtop(string) for string
            in split_search_levels_response_creators(creators_string)
        ]

        songs = [
            SongModel.from_robtop(string) for string
            in split_search_levels_response_songs(songs_string)
        ]

        page = PageModel.from_robtop(page_string)

        return cls(levels=levels, creators=creators, songs=songs, page=page, hash=hash)

    def to_robtop(self) -> str:
        values = (
            concat_search_levels_response_levels(level.to_robtop() for level in self.levels),
            concat_search_levels_response_creators(creator.to_robtop() for creator in self.creators),
            concat_search_levels_response_songs(song.to_robtop() for song in self.songs),
            self.page.to_robtop(),
            self.hash,
        )

        return concat_search_levels_response(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return SEARCH_LEVELS_RESPONSE_SEPARATOR in string


SUR = TypeVar("SUR", bound="SearchUsersResponseModel")


@define()
class SearchUsersResponseModel(Model):
    users: List[SearchUserModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[SUR], string: str) -> SUR:
        users_string, page_string = split_search_users_response(string)

        users = [
            SearchUserModel.from_robtop(string)
            for string in split_search_users_response_users(users_string)
        ]

        page = PageModel.from_robtop(page_string)

        return cls(users=users, page=page)

    def to_robtop(self) -> str:
        values = (
            concat_search_users_response_users(user.to_robtop() for user in self.users),
            self.page.to_robtop(),
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
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[MR], string: str) -> MR:
        messages_string, page_string = split_messages_response(string)

        messages = [
            MessageModel.from_robtop(string, content_present=False)
            for string in split_messages_response_messages(messages_string)
        ]

        page = PageModel.from_robtop(page_string)

        return cls(messages=messages, page=page)

    def to_robtop(self) -> str:
        values = (
            concat_messages_response_messages(message.to_robtop() for message in self.messages),
            self.page.to_robtop(),
        )

        return concat_messages_response(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return MESSAGES_RESPONSE_SEPARATOR in string


FRR = TypeVar("FRR", bound="FriendRequestsResponseModel")


@define()
class FriendRequestsResponseModel(Model):
    friend_requests: List[FriendRequestModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[FRR], string: str) -> FRR:
        friend_requests_string, page_string = split_friend_requests_response(string)

        friend_requests = [
            FriendRequestModel.from_robtop(string)
            for string in split_friend_requests_response_friend_requests(friend_requests_string)
        ]

        page = PageModel.from_robtop(page_string)

        return cls(friend_requests=friend_requests, page=page)

    def to_robtop(self) -> str:
        values = (
            concat_friend_requests_response_friend_requests(
                friend_request.to_robtop() for friend_request in self.friend_requests
            ),
            self.page.to_robtop(),
        )

        return concat_friend_requests_response(values)

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
