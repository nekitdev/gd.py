from typing import Iterator, List, Optional, Type, TypeVar
from urllib.parse import quote, unquote

from attrs import define, field
from iters import iter
from typing_extensions import Protocol
from yarl import URL

from gd.api.editor import Editor
from gd.color import Color
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
    DEFAULT_RECORD,
    DEFAULT_SCORE,
    DEFAULT_SECRET_COINS,
    DEFAULT_SENT,
    DEFAULT_SIZE,
    DEFAULT_SPAM,
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
from gd.date_time import DateTime, Duration, date_time_from_human, date_time_to_human, utc_now
from gd.decorators import cache_by
from gd.difficulty_parameters import DifficultyParameters, VALUE_TO_DEMON_DIFFICULTY, DEMON_DIFFICULTY_TO_VALUE
from gd.encoding import (
    decode_base64_string_url_safe,
    decode_robtop_string,
    encode_base64_string_url_safe,
    encode_robtop_string,
    generate_level_seed,
    sha1_string_with_salt,
    unzip_level_string,
    zip_level_string,
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
    FRIEND_REQUEST_SEPARATOR,
    LEADERBOARD_RESPONSE_USERS_SEPARATOR,
    LEADERBOARD_USER_SEPARATOR,
    LEVEL_COMMENT_INNER_SEPARATOR,
    LEVEL_COMMENT_SEPARATOR,
    LEVEL_COMMENT_USER_SEPARATOR,
    LEVEL_COMMENTS_RESPONSE_SEPARATOR,
    LEVEL_LEADERBOARD_RESPONSE_USERS_SEPARATOR,
    LEVEL_LEADERBOARD_USER_SEPARATOR,
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
    USER_COMMENT_SEPARATOR,
    USER_COMMENTS_RESPONSE_SEPARATOR,
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
    concat_level_comment,
    concat_level_comment_inner,
    concat_level_comment_user,
    concat_level_comments_response,
    concat_level_comments_response_comments,
    concat_level_leaderboard_response_users,
    concat_level_leaderboard_user,
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
    concat_user_comment,
    concat_user_comments_response,
    concat_user_comments_response_comments,
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
    split_level_comment,
    split_level_comment_inner,
    split_level_comment_user,
    split_level_comments_response,
    split_level_comments_response_comments,
    split_level_leaderboard_response_users,
    split_level_leaderboard_user,
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
    split_user_comment,
    split_user_comments_response,
    split_user_comments_response_comments,
)
from gd.password import Password
from gd.robtop import RobTop
from gd.string_utils import concat_empty
from gd.typing import DynamicTuple
from gd.versions import CURRENT_GAME_VERSION, GameVersion

__all__ = (
    "Model",
    "ChestModel",
    "CommentBannedModel",
    "CreatorModel",
    "FriendRequestModel",
    "GauntletModel",
    "LevelCommentModel",
    "LevelCommentUserModel",
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
    "UserCommentModel",
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
        id_index: int = SONG_ID,
        name_index: int = SONG_NAME,
        artist_name_index: int = SONG_ARTIST_NAME,
        artist_id_index: int = SONG_ARTIST_ID,
        size_index: int = SONG_SIZE,
        youtube_video_id_index: int = SONG_YOUTUBE_VIDEO_ID,
        youtube_channel_id_index: int = SONG_YOUTUBE_CHANNEL_ID,
        unknown_index: int = SONG_UNKNOWN,
        download_url_index: int = SONG_DOWNLOAD_URL,
        # defaults
        id_default: int = DEFAULT_ID,
        name_default: str = UNKNOWN,
        artist_name_default: str = UNKNOWN,
        artist_id_default: int = DEFAULT_ID,
        size_default: float = DEFAULT_SIZE,
        youtube_video_id_default: str = EMPTY,
        youtube_channel_id_default: str = EMPTY,
        unknown_default: str = EMPTY,
    ) -> S:
        mapping = split_song(string)

        download_url_string = mapping.get(download_url_index)

        download_url = URL(unquote(download_url_string)) if download_url_string else None

        return cls(
            id=parse_get_or(int, id_default, mapping.get(id_index)),
            name=mapping.get(name_index, name_default),
            artist_name=mapping.get(artist_name_index, artist_name_default),
            artist_id=parse_get_or(int, artist_id_default, mapping.get(artist_id_index)),
            size=parse_get_or(float, size_default, mapping.get(size_index)),
            youtube_video_id=mapping.get(youtube_video_id_index, youtube_video_id_default),
            youtube_channel_id=mapping.get(youtube_channel_id_index, youtube_channel_id_default),
            unknown=mapping.get(unknown_index, unknown_default),
            download_url=download_url,
        )

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return SONG_SEPARATOR in string

    def to_robtop(
        self,
        *,  # bring indexes into the scope
        id_index: int = SONG_ID,
        name_index: int = SONG_NAME,
        artist_name_index: int = SONG_ARTIST_NAME,
        artist_id_index: int = SONG_ARTIST_ID,
        size_index: int = SONG_SIZE,
        youtube_video_id_index: int = SONG_YOUTUBE_VIDEO_ID,
        youtube_channel_id_index: int = SONG_YOUTUBE_CHANNEL_ID,
        unknown_index: int = SONG_UNKNOWN,
        download_url_index: int = SONG_DOWNLOAD_URL,
    ) -> str:
        mapping = {
            id_index: str(self.id),
            name_index: self.name,
            artist_name_index: self.artist_name,
            artist_id_index: str(self.artist_id),
            size_index: float_str(self.size),
            youtube_video_id_index: self.youtube_video_id,
            youtube_channel_id_index: self.youtube_channel_id,
            unknown_index: self.unknown,
            download_url_index: quote(str(self.download_url or EMPTY)),
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
        values = (str(self.account_id), str(self.id))

        return concat_login(values)


CRT = TypeVar("CRT", bound="CreatorModel")


@define()
class CreatorModel(Model):
    id: int = DEFAULT_ID
    name: str = UNKNOWN
    account_id: int = DEFAULT_ID

    @classmethod
    def from_robtop(cls: Type[CRT], string: str) -> CRT:
        id_string, name, account_id_string = split_creator(string)

        return cls(int(id_string), name, int(account_id_string))

    def to_robtop(self) -> str:
        values = (str(self.id), self.name, str(self.account_id))

        return concat_creator(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return CREATOR_SEPARATOR in string


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
        name_index: int = SEARCH_USER_NAME,
        id_index: int = SEARCH_USER_ID,
        stars_index: int = SEARCH_USER_STARS,
        demons_index: int = SEARCH_USER_DEMONS,
        rank_index: int = SEARCH_USER_RANK,
        creator_points_index: int = SEARCH_USER_CREATOR_POINTS,
        icon_id_index: int = SEARCH_USER_ICON_ID,
        color_1_id_index: int = SEARCH_USER_COLOR_1_ID,
        color_2_id_index: int = SEARCH_USER_COLOR_2_ID,
        secret_coins_index: int = SEARCH_USER_SECRET_COINS,
        icon_type_index: int = SEARCH_USER_ICON_TYPE,
        glow_index: int = SEARCH_USER_GLOW,
        account_id_index: int = SEARCH_USER_ACCOUNT_ID,
        user_coins_index: int = SEARCH_USER_USER_COINS,
        # defaults
        name_default: str = UNKNOWN,
        id_default: int = DEFAULT_ID,
        stars_default: int = DEFAULT_STARS,
        demons_default: int = DEFAULT_DEMONS,
        rank_default: int = DEFAULT_RANK,
        creator_points_default: int = DEFAULT_CREATOR_POINTS,
        icon_id_default: int = DEFAULT_ID,
        color_1_id_default: int = DEFAULT_COLOR_2_ID,
        color_2_id_default: int = DEFAULT_COLOR_2_ID,
        secret_coins_default: int = DEFAULT_SECRET_COINS,
        icon_type_default: IconType = IconType.DEFAULT,
        glow_default: bool = DEFAULT_GLOW,
        account_id_default: int = DEFAULT_ID,
        user_coins_default: int = DEFAULT_USER_COINS,
    ) -> SU:
        mapping = split_search_user(string)

        rank_string = mapping.get(rank_index)

        if rank_string:
            rank = int(rank_string)

        else:
            rank = rank_default

        return cls(
            name=mapping.get(name_index, name_default),
            id=parse_get_or(int, id_default, mapping.get(id_index)),
            stars=parse_get_or(int, stars_default, mapping.get(stars_index)),
            demons=parse_get_or(int, demons_default, mapping.get(demons_index)),
            rank=rank,
            creator_points=parse_get_or(
                int,
                creator_points_default,
                mapping.get(creator_points_index),
            ),
            icon_id=parse_get_or(int, icon_id_default, mapping.get(icon_id_index)),
            color_1_id=parse_get_or(int, color_1_id_default, mapping.get(color_1_id_index)),
            color_2_id=parse_get_or(int, color_2_id_default, mapping.get(color_2_id_index)),
            secret_coins=parse_get_or(int, secret_coins_default, mapping.get(secret_coins_index)),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                icon_type_default,
                mapping.get(icon_type_index),
            ),
            glow=parse_get_or(int_bool, glow_default, mapping.get(glow_index)),
            account_id=parse_get_or(int, account_id_default, mapping.get(account_id_index)),
            user_coins=parse_get_or(int, user_coins_default, mapping.get(user_coins_index)),
        )

    def to_robtop(
        self,
        name_index: int = SEARCH_USER_NAME,
        id_index: int = SEARCH_USER_ID,
        stars_index: int = SEARCH_USER_STARS,
        demons_index: int = SEARCH_USER_DEMONS,
        rank_index: int = SEARCH_USER_RANK,
        creator_points_index: int = SEARCH_USER_CREATOR_POINTS,
        icon_id_index: int = SEARCH_USER_ICON_ID,
        color_1_id_index: int = SEARCH_USER_COLOR_1_ID,
        color_2_id_index: int = SEARCH_USER_COLOR_2_ID,
        secret_coins_index: int = SEARCH_USER_SECRET_COINS,
        icon_type_index: int = SEARCH_USER_ICON_TYPE,
        glow_index: int = SEARCH_USER_GLOW,
        account_id_index: int = SEARCH_USER_ACCOUNT_ID,
        user_coins_index: int = SEARCH_USER_USER_COINS,
    ) -> str:
        glow = self.glow

        glow += glow  # type: ignore

        mapping = {
            name_index: self.name,
            id_index: str(self.id),
            stars_index: str(self.stars),
            demons_index: str(self.demons),
            rank_index: str(self.rank),
            creator_points_index: str(self.creator_points),
            icon_id_index: str(self.icon_id),
            color_1_id_index: str(self.color_1_id),
            color_2_id_index: str(self.color_2_id),
            secret_coins_index: str(self.secret_coins),
            icon_type_index: str(self.icon_type.value),
            glow_index: str(glow),
            account_id_index: str(self.account_id),
            user_coins_index: str(self.user_coins),
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
        name_index: int = PROFILE_NAME,
        id_index: int = PROFILE_ID,
        stars_index: int = PROFILE_STARS,
        demons_index: int = PROFILE_DEMONS,
        creator_points_index: int = PROFILE_CREATOR_POINTS,
        color_1_id_index: int = PROFILE_COLOR_1_ID,
        color_2_id_index: int = PROFILE_COLOR_2_ID,
        secret_coins_index: int = PROFILE_SECRET_COINS,
        account_id_index: int = PROFILE_ACCOUNT_ID,
        user_coins_index: int = PROFILE_USER_COINS,
        message_state_index: int = PROFILE_MESSAGE_STATE,
        friend_request_state_index: int = PROFILE_FRIEND_REQUEST_STATE,
        youtube_index: int = PROFILE_YOUTUBE,
        cube_id_index: int = PROFILE_CUBE_ID,
        ship_id_index: int = PROFILE_SHIP_ID,
        ball_id_index: int = PROFILE_BALL_ID,
        ufo_id_index: int = PROFILE_UFO_ID,
        wave_id_index: int = PROFILE_WAVE_ID,
        robot_id_index: int = PROFILE_ROBOT_ID,
        glow_index: int = PROFILE_GLOW,
        active_index: int = PROFILE_ACTIVE,
        rank_index: int = PROFILE_RANK,
        friend_state_index: int = PROFILE_FRIEND_STATE,
        new_messages_index: int = PROFILE_NEW_MESSAGES,
        new_friend_requests_index: int = PROFILE_NEW_FRIEND_REQUESTS,
        new_friends_index: int = PROFILE_NEW_FRIENDS,
        spider_id_index: int = PROFILE_SPIDER_ID,
        twitter_index: int = PROFILE_TWITTER,
        twitch_index: int = PROFILE_TWITCH,
        diamonds_index: int = PROFILE_DIAMONDS,
        explosion_id_index: int = PROFILE_EXPLOSION_ID,
        role_index: int = PROFILE_ROLE,
        comment_state_index: int = PROFILE_COMMENT_STATE,
        # defaults
        name_default: str = UNKNOWN,
        id_default: int = DEFAULT_ID,
        stars_default: int = DEFAULT_STARS,
        demons_default: int = DEFAULT_DEMONS,
        creator_points_default: int = DEFAULT_CREATOR_POINTS,
        color_1_id_default: int = DEFAULT_COLOR_1_ID,
        color_2_id_default: int = DEFAULT_COLOR_2_ID,
        secret_coins_default: int = DEFAULT_SECRET_COINS,
        account_id_default: int = DEFAULT_ID,
        user_coins_default: int = DEFAULT_USER_COINS,
        message_state_default: MessageState = MessageState.DEFAULT,
        friend_request_state_default: FriendRequestState = FriendRequestState.DEFAULT,
        youtube_default: Optional[str] = None,
        cube_id_default: int = DEFAULT_ICON_ID,
        ship_id_default: int = DEFAULT_ICON_ID,
        ball_id_default: int = DEFAULT_ICON_ID,
        ufo_id_default: int = DEFAULT_ICON_ID,
        wave_id_default: int = DEFAULT_ICON_ID,
        robot_id_default: int = DEFAULT_ICON_ID,
        glow_default: bool = DEFAULT_GLOW,
        active_default: bool = DEFAULT_ACTIVE,
        rank_default: int = DEFAULT_RANK,
        friend_state_default: FriendState = FriendState.DEFAULT,
        new_messages_default: int = DEFAULT_NEW,
        new_friend_requests_default: int = DEFAULT_NEW,
        new_friends_default: int = DEFAULT_NEW,
        spider_id_default: int = DEFAULT_ICON_ID,
        twitter_default: Optional[str] = None,
        twitch_default: Optional[str] = None,
        diamonds_default: int = DEFAULT_DIAMONDS,
        explosion_id_default: int = DEFAULT_ICON_ID,
        role_default: Role = Role.DEFAULT,
        comment_state_default: CommentState = CommentState.DEFAULT,
    ) -> P:
        mapping = split_profile(string)

        return cls(
            name=mapping.get(name_index, name_default),
            id=parse_get_or(int, id_default, mapping.get(id_index)),
            stars=parse_get_or(int, stars_default, mapping.get(stars_index)),
            demons=parse_get_or(int, demons_default, mapping.get(demons_index)),
            creator_points=parse_get_or(
                int, creator_points_default, mapping.get(creator_points_index)
            ),
            color_1_id=parse_get_or(int, color_1_id_default, mapping.get(color_1_id_index)),
            color_2_id=parse_get_or(int, color_2_id_default, mapping.get(color_2_id_index)),
            secret_coins=parse_get_or(int, secret_coins_default, mapping.get(secret_coins_index)),
            account_id=parse_get_or(int, account_id_default, mapping.get(account_id_index)),
            user_coins=parse_get_or(int, user_coins_default, mapping.get(user_coins_index)),
            message_state=parse_get_or(
                partial_parse_enum(int, MessageState),
                message_state_default,
                mapping.get(message_state_index),
            ),
            friend_request_state=parse_get_or(
                partial_parse_enum(int, FriendRequestState),
                friend_request_state_default,
                mapping.get(friend_request_state_index),
            ),
            youtube=mapping.get(youtube_index) or youtube_default,
            cube_id=parse_get_or(int, cube_id_default, mapping.get(cube_id_index)),
            ship_id=parse_get_or(int, ship_id_default, mapping.get(ship_id_index)),
            ball_id=parse_get_or(int, ball_id_default, mapping.get(ball_id_index)),
            ufo_id=parse_get_or(int, ufo_id_default, mapping.get(ufo_id_index)),
            wave_id=parse_get_or(int, wave_id_default, mapping.get(wave_id_index)),
            robot_id=parse_get_or(int, robot_id_default, mapping.get(robot_id_index)),
            glow=parse_get_or(int_bool, glow_default, mapping.get(glow_index)),
            active=parse_get_or(int_bool, active_default, mapping.get(active_index)),
            rank=parse_get_or(int, rank_default, mapping.get(rank_index)),
            friend_state=parse_get_or(
                partial_parse_enum(int, FriendState),
                friend_state_default,
                mapping.get(friend_state_index),
            ),
            new_messages=parse_get_or(int, new_messages_default, mapping.get(new_messages_index)),
            new_friend_requests=parse_get_or(
                int,
                new_friend_requests_default,
                mapping.get(new_friend_requests_index),
            ),
            new_friends=parse_get_or(int, new_friends_default, mapping.get(new_friends_index)),
            spider_id=parse_get_or(int, spider_id_default, mapping.get(spider_id_index)),
            twitter=mapping.get(twitter_index) or twitter_default,
            twitch=mapping.get(twitch_index) or twitch_default,
            diamonds=parse_get_or(int, diamonds_default, mapping.get(diamonds_index)),
            explosion_id=parse_get_or(int, explosion_id_default, mapping.get(explosion_id_index)),
            role=parse_get_or(partial_parse_enum(int, Role), role_default, mapping.get(role_index)),
            comment_state=parse_get_or(
                partial_parse_enum(int, CommentState),
                comment_state_default,
                mapping.get(comment_state_index),
            ),
        )

    def to_robtop(
        self,
        name_index: int = PROFILE_NAME,
        id_index: int = PROFILE_ID,
        stars_index: int = PROFILE_STARS,
        demons_index: int = PROFILE_DEMONS,
        creator_points_index: int = PROFILE_CREATOR_POINTS,
        color_1_id_index: int = PROFILE_COLOR_1_ID,
        color_2_id_index: int = PROFILE_COLOR_2_ID,
        secret_coins_index: int = PROFILE_SECRET_COINS,
        account_id_index: int = PROFILE_ACCOUNT_ID,
        user_coins_index: int = PROFILE_USER_COINS,
        message_state_index: int = PROFILE_MESSAGE_STATE,
        friend_request_state_index: int = PROFILE_FRIEND_REQUEST_STATE,
        youtube_index: int = PROFILE_YOUTUBE,
        cube_id_index: int = PROFILE_CUBE_ID,
        ship_id_index: int = PROFILE_SHIP_ID,
        ball_id_index: int = PROFILE_BALL_ID,
        ufo_id_index: int = PROFILE_UFO_ID,
        wave_id_index: int = PROFILE_WAVE_ID,
        robot_id_index: int = PROFILE_ROBOT_ID,
        glow_index: int = PROFILE_GLOW,
        active_index: int = PROFILE_ACTIVE,
        rank_index: int = PROFILE_RANK,
        friend_state_index: int = PROFILE_FRIEND_STATE,
        new_messages_index: int = PROFILE_NEW_MESSAGES,
        new_friend_requests_index: int = PROFILE_NEW_FRIEND_REQUESTS,
        new_friends_index: int = PROFILE_NEW_FRIENDS,
        spider_id_index: int = PROFILE_SPIDER_ID,
        twitter_index: int = PROFILE_TWITTER,
        twitch_index: int = PROFILE_TWITCH,
        diamonds_index: int = PROFILE_DIAMONDS,
        explosion_id_index: int = PROFILE_EXPLOSION_ID,
        role_index: int = PROFILE_ROLE,
        comment_state_index: int = PROFILE_COMMENT_STATE,
    ) -> str:
        mapping = {
            name_index: self.name,
            id_index: str(self.id),
            stars_index: str(self.stars),
            demons_index: str(self.demons),
            creator_points_index: str(self.creator_points),
            color_1_id_index: str(self.color_1_id),
            color_2_id_index: str(self.color_2_id),
            secret_coins_index: str(self.secret_coins),
            account_id_index: str(self.account_id),
            user_coins_index: str(self.user_coins),
            message_state_index: str(self.message_state.value),
            friend_request_state_index: str(self.friend_request_state.value),
            youtube_index: self.youtube or EMPTY,
            cube_id_index: str(self.cube_id),
            ship_id_index: str(self.ship_id),
            ball_id_index: str(self.ball_id),
            ufo_id_index: str(self.ufo_id),
            wave_id_index: str(self.wave_id),
            robot_id_index: str(self.robot_id),
            glow_index: str(int(self.glow)),
            active_index: str(int(self.active)),
            rank_index: str(int(self.rank)),
            friend_state_index: str(self.friend_state.value),
            new_messages_index: str(self.new_messages),
            new_friend_requests_index: str(self.new_friend_requests),
            new_friends_index: str(self.new_friends),
            spider_id_index: str(self.spider_id),
            twitter_index: self.twitter or EMPTY,
            twitch_index: self.twitch or EMPTY,
            diamonds_index: str(self.diamonds),
            explosion_id_index: str(self.explosion_id),
            role_index: str(self.role.value),
            comment_state_index: str(self.comment_state.value),
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
        name_index: int = RELATIONSHIP_USER_NAME,
        id_index: int = RELATIONSHIP_USER_ID,
        icon_id_index: int = RELATIONSHIP_USER_ICON_ID,
        color_1_id_index: int = RELATIONSHIP_USER_COLOR_1_ID,
        color_2_id_index: int = RELATIONSHIP_USER_COLOR_2_ID,
        icon_type_index: int = RELATIONSHIP_USER_ICON_TYPE,
        glow_index: int = RELATIONSHIP_USER_GLOW,
        account_id_index: int = RELATIONSHIP_USER_ACCOUNT_ID,
        message_state_index: int = RELATIONSHIP_USER_MESSAGE_STATE,
        name_default: str = UNKNOWN,
        id_default: int = DEFAULT_ID,
        icon_id_default: int = DEFAULT_ICON_ID,
        color_1_id_default: int = DEFAULT_COLOR_1_ID,
        color_2_id_default: int = DEFAULT_COLOR_2_ID,
        icon_type_default: IconType = IconType.DEFAULT,
        glow_default: bool = DEFAULT_GLOW,
        account_id_default: int = DEFAULT_ID,
        message_state_default: MessageState = MessageState.DEFAULT,
    ) -> RU:
        mapping = split_relationship_user(string)

        return cls(
            name=mapping.get(name_index, name_default),
            id=parse_get_or(int, id_default, mapping.get(id_index)),
            icon_id=parse_get_or(int, icon_id_default, mapping.get(icon_id_index)),
            color_1_id=parse_get_or(
                int,
                color_1_id_default,
                mapping.get(color_1_id_index),
            ),
            color_2_id=parse_get_or(
                int,
                color_2_id_default,
                mapping.get(color_2_id_index),
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                icon_type_default,
                mapping.get(icon_type_index),
            ),
            glow=parse_get_or(int_bool, glow_default, mapping.get(glow_index)),
            account_id=parse_get_or(
                int,
                account_id_default,
                mapping.get(account_id_index),
            ),
            message_state=parse_get_or(
                partial_parse_enum(int, MessageState),
                message_state_default,
                mapping.get(message_state_index),
            ),
        )

    def to_robtop(
        self,
        name_index: int = RELATIONSHIP_USER_NAME,
        id_index: int = RELATIONSHIP_USER_ID,
        icon_id_index: int = RELATIONSHIP_USER_ICON_ID,
        color_1_id_index: int = RELATIONSHIP_USER_COLOR_1_ID,
        color_2_id_index: int = RELATIONSHIP_USER_COLOR_2_ID,
        icon_type_index: int = RELATIONSHIP_USER_ICON_TYPE,
        glow_index: int = RELATIONSHIP_USER_GLOW,
        account_id_index: int = RELATIONSHIP_USER_ACCOUNT_ID,
        message_state_index: int = RELATIONSHIP_USER_MESSAGE_STATE,
    ) -> str:
        mapping = {
            name_index: str(self.name),
            id_index: str(self.id),
            icon_id_index: str(self.icon_id),
            color_1_id_index: str(self.color_1_id),
            color_2_id_index: str(self.color_2_id),
            icon_type_index: str(self.icon_type.value),
            glow_index: str(int(self.glow)),
            account_id_index: str(self.account_id),
            message_state_index: str(self.message_state.value),
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
        name_index: int = LEADERBOARD_USER_NAME,
        id_index: int = LEADERBOARD_USER_ID,
        stars_index: int = LEADERBOARD_USER_STARS,
        demons_index: int = LEADERBOARD_USER_DEMONS,
        place_index: int = LEADERBOARD_USER_PLACE,
        creator_points_index: int = LEADERBOARD_USER_CREATOR_POINTS,
        icon_id_index: int = LEADERBOARD_USER_ICON_ID,
        color_1_id_index: int = LEADERBOARD_USER_COLOR_1_ID,
        color_2_id_index: int = LEADERBOARD_USER_COLOR_2_ID,
        secret_coins_index: int = LEADERBOARD_USER_SECRET_COINS,
        icon_type_index: int = LEADERBOARD_USER_ICON_TYPE,
        glow_index: int = LEADERBOARD_USER_GLOW,
        account_id_index: int = LEADERBOARD_USER_ACCOUNT_ID,
        user_coins_index: int = LEADERBOARD_USER_USER_COINS,
        diamonds_index: int = LEADERBOARD_USER_DIAMONDS,
        # defaults
        name_default: str = UNKNOWN,
        id_default: int = DEFAULT_ID,
        stars_default: int = DEFAULT_STARS,
        demons_default: int = DEFAULT_DEMONS,
        place_default: int = DEFAULT_PLACE,
        creator_points_default: int = DEFAULT_CREATOR_POINTS,
        icon_id_default: int = DEFAULT_ICON_ID,
        color_1_id_default: int = DEFAULT_COLOR_1_ID,
        color_2_id_default: int = DEFAULT_COLOR_2_ID,
        secret_coins_default: int = DEFAULT_SECRET_COINS,
        icon_type_default: IconType = IconType.DEFAULT,
        glow_default: bool = DEFAULT_GLOW,
        account_id_default: int = DEFAULT_ID,
        user_coins_default: int = DEFAULT_USER_COINS,
        diamonds_default: int = DEFAULT_DIAMONDS,
    ) -> LU:
        mapping = split_leaderboard_user(string)

        return cls(
            name=mapping.get(name_index, name_default),
            id=parse_get_or(int, id_default, mapping.get(id_index)),
            stars=parse_get_or(int, stars_default, mapping.get(stars_index)),
            demons=parse_get_or(int, demons_default, mapping.get(demons_index)),
            place=parse_get_or(int, place_default, mapping.get(place_index)),
            creator_points=parse_get_or(
                int,
                creator_points_default,
                mapping.get(creator_points_index),
            ),
            icon_id=parse_get_or(int, icon_id_default, mapping.get(icon_id_index)),
            color_1_id=parse_get_or(
                int,
                color_1_id_default,
                mapping.get(color_1_id_index),
            ),
            color_2_id=parse_get_or(
                int,
                color_2_id_default,
                mapping.get(color_2_id_index),
            ),
            secret_coins=parse_get_or(
                int,
                secret_coins_default,
                mapping.get(secret_coins_index),
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                icon_type_default,
                mapping.get(icon_type_index),
            ),
            glow=parse_get_or(int_bool, glow_default, mapping.get(glow_index)),
            account_id=parse_get_or(
                int,
                account_id_default,
                mapping.get(account_id_index),
            ),
            user_coins=parse_get_or(
                int,
                user_coins_default,
                mapping.get(user_coins_index),
            ),
            diamonds=parse_get_or(int, diamonds_default, mapping.get(diamonds_index)),
        )

    def to_robtop(
        self,
        name_index: int = LEADERBOARD_USER_NAME,
        id_index: int = LEADERBOARD_USER_ID,
        stars_index: int = LEADERBOARD_USER_STARS,
        demons_index: int = LEADERBOARD_USER_DEMONS,
        place_index: int = LEADERBOARD_USER_PLACE,
        creator_points_index: int = LEADERBOARD_USER_CREATOR_POINTS,
        icon_id_index: int = LEADERBOARD_USER_ICON_ID,
        color_1_id_index: int = LEADERBOARD_USER_COLOR_1_ID,
        color_2_id_index: int = LEADERBOARD_USER_COLOR_2_ID,
        secret_coins_index: int = LEADERBOARD_USER_SECRET_COINS,
        icon_type_index: int = LEADERBOARD_USER_ICON_TYPE,
        glow_index: int = LEADERBOARD_USER_GLOW,
        account_id_index: int = LEADERBOARD_USER_ACCOUNT_ID,
        user_coins_index: int = LEADERBOARD_USER_USER_COINS,
        diamonds_index: int = LEADERBOARD_USER_DIAMONDS,
    ) -> str:
        glow = self.glow

        glow += glow  # type: ignore

        mapping = {
            name_index: self.name,
            id_index: str(self.id),
            stars_index: str(self.stars),
            place_index: str(self.place),
            demons_index: str(self.demons),
            creator_points_index: str(self.creator_points),
            icon_id_index: str(self.icon_id),
            color_1_id_index: str(self.color_1_id),
            color_2_id_index: str(self.color_2_id),
            secret_coins_index: str(self.secret_coins),
            icon_type_index: str(self.icon_type.value),
            glow_index: str(glow),
            account_id_index: str(self.account_id),
            user_coins_index: str(self.user_coins),
            diamonds_index: str(self.diamonds),
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
    cooldown: Duration = field(factory=Duration)

    @classmethod
    def from_robtop(cls: Type[TI], string: str, type: TimelyType = TimelyType.DEFAULT) -> TI:
        timely_id, cooldown_seconds = iter(split_timely_info(string)).map(int).tuple()

        return cls(
            id=timely_id % TIMELY_ID_ADD, type=type, cooldown=Duration(seconds=cooldown_seconds)
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
    created_at: DateTime = field(factory=utc_now)
    read: bool = field(default=DEFAULT_READ)
    sent: bool = field(default=DEFAULT_SENT)

    content_present: bool = field(default=DEFAULT_CONTENT_PRESENT)

    @classmethod
    def from_robtop(
        cls: Type[M],
        string: str,
        content_present: bool = DEFAULT_CONTENT_PRESENT,
        # indexes
        id_index: int = MESSAGE_ID,
        account_id_index: int = MESSAGE_ACCOUNT_ID,
        user_id_index: int = MESSAGE_USER_ID,
        subject_index: int = MESSAGE_SUBJECT,
        content_index: int = MESSAGE_CONTENT,
        name_index: int = MESSAGE_NAME,
        created_at_index: int = MESSAGE_CREATED_AT,
        read_index: int = MESSAGE_READ,
        sent_index: int = MESSAGE_SENT,
        # defaults
        id_default: int = DEFAULT_ID,
        account_id_default: int = DEFAULT_ID,
        user_id_default: int = DEFAULT_ID,
        subject_default: str = EMPTY,
        content_default: str = EMPTY,
        name_default: str = UNKNOWN,
        created_at_default: Optional[DateTime] = None,
        read_default: bool = DEFAULT_READ,
        sent_default: bool = DEFAULT_SENT,
    ) -> M:
        if created_at_default is None:
            created_at_default = utc_now()

        mapping = split_message(string)

        return cls(
            id=parse_get_or(int, id_default, mapping.get(id_index)),
            account_id=parse_get_or(int, account_id_default, mapping.get(account_id_index)),
            user_id=parse_get_or(
                int,
                user_id_default,
                mapping.get(user_id_index),
            ),
            subject=decode_base64_string_url_safe(mapping.get(subject_index, subject_default)),
            content=decode_robtop_string(mapping.get(content_index, content_default), Key.MESSAGE),
            name=mapping.get(name_index, name_default),
            created_at=parse_get_or(
                date_time_from_human,
                created_at_default,
                mapping.get(created_at_index),
                ignore_errors=True,
            ),
            read=parse_get_or(int_bool, read_default, mapping.get(read_index)),
            sent=parse_get_or(int_bool, sent_default, mapping.get(sent_index)),
            content_present=content_present,
        )

    def to_robtop(
        self,
        id_index: int = MESSAGE_ID,
        account_id_index: int = MESSAGE_ACCOUNT_ID,
        user_id_index: int = MESSAGE_USER_ID,
        subject_index: int = MESSAGE_SUBJECT,
        content_index: int = MESSAGE_CONTENT,
        name_index: int = MESSAGE_NAME,
        created_at_index: int = MESSAGE_CREATED_AT,
        read_index: int = MESSAGE_READ,
        sent_index: int = MESSAGE_SENT,
    ) -> str:
        mapping = {
            id_index: str(self.id),
            account_id_index: str(self.account_id),
            user_id_index: str(self.user_id),
            subject_index: encode_base64_string_url_safe(self.subject),
            content_index: encode_robtop_string(self.content, Key.MESSAGE),
            name_index: self.name,
            created_at_index: date_time_to_human(self.created_at),
            read_index: str(int(self.read)),
            sent_index: str(int(self.sent)),
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
    created_at: DateTime = field(factory=utc_now)
    unread: bool = field(default=DEFAULT_UNREAD)

    @classmethod
    def from_robtop(
        cls: Type[FR],
        string: str,
        # indexes
        name_index: int = FRIEND_REQUEST_NAME,
        user_id_index: int = FRIEND_REQUEST_USER_ID,
        icon_id_index: int = FRIEND_REQUEST_ICON_ID,
        color_1_id_index: int = FRIEND_REQUEST_COLOR_1_ID,
        color_2_id_index: int = FRIEND_REQUEST_COLOR_2_ID,
        icon_type_index: int = FRIEND_REQUEST_ICON_TYPE,
        glow_index: int = FRIEND_REQUEST_GLOW,
        account_id_index: int = FRIEND_REQUEST_ACCOUNT_ID,
        id_index: int = FRIEND_REQUEST_ID,
        content_index: int = FRIEND_REQUEST_CONTENT,
        created_at_index: int = FRIEND_REQUEST_CREATED_AT,
        unread_index: int = FRIEND_REQUEST_UNREAD,
        # defaults
        name_default: str = UNKNOWN,
        user_id_default: int = DEFAULT_ID,
        icon_id_default: int = DEFAULT_ICON_ID,
        color_1_id_default: int = DEFAULT_COLOR_1_ID,
        color_2_id_default: int = DEFAULT_COLOR_2_ID,
        icon_type_default: IconType = IconType.DEFAULT,
        glow_default: bool = DEFAULT_GLOW,
        account_id_default: int = DEFAULT_ID,
        id_default: int = DEFAULT_ID,
        content_default: str = EMPTY,
        created_at_default: Optional[DateTime] = None,
        unread_default: bool = DEFAULT_UNREAD,
    ) -> FR:
        if created_at_default is None:
            created_at_default = utc_now()

        mapping = split_friend_request(string)

        return cls(
            name=mapping.get(name_index, name_default),
            user_id=parse_get_or(int, user_id_default, mapping.get(user_id_index)),
            icon_id=parse_get_or(int, icon_id_default, mapping.get(icon_id_index)),
            color_1_id=parse_get_or(
                int,
                color_1_id_default,
                mapping.get(color_1_id_index),
            ),
            color_2_id=parse_get_or(
                int,
                color_2_id_default,
                mapping.get(color_2_id_index),
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                icon_type_default,
                mapping.get(icon_type_index),
            ),
            glow=parse_get_or(int_bool, glow_default, mapping.get(glow_index)),
            account_id=parse_get_or(int, account_id_default, mapping.get(account_id_index)),
            id=parse_get_or(int, id_default, mapping.get(id_index)),
            content=decode_base64_string_url_safe(mapping.get(content_index, content_default)),
            created_at=parse_get_or(
                date_time_from_human,
                created_at_default,
                mapping.get(created_at_index),
                ignore_errors=True,
            ),
            unread=parse_get_or(int_bool, unread_default, mapping.get(unread_index)),
        )

    def to_robtop(
        self,
        name_index: int = FRIEND_REQUEST_NAME,
        user_id_index: int = FRIEND_REQUEST_USER_ID,
        icon_id_index: int = FRIEND_REQUEST_ICON_ID,
        color_1_id_index: int = FRIEND_REQUEST_COLOR_1_ID,
        color_2_id_index: int = FRIEND_REQUEST_COLOR_2_ID,
        icon_type_index: int = FRIEND_REQUEST_ICON_TYPE,
        glow_index: int = FRIEND_REQUEST_GLOW,
        account_id_index: int = FRIEND_REQUEST_ACCOUNT_ID,
        id_index: int = FRIEND_REQUEST_ID,
        content_index: int = FRIEND_REQUEST_CONTENT,
        created_at_index: int = FRIEND_REQUEST_CREATED_AT,
        unread_index: int = FRIEND_REQUEST_UNREAD,
    ) -> str:
        glow = self.glow

        glow += glow  # type: ignore

        unread = EMPTY if self.is_read() else str(int(self.unread))

        mapping = {
            name_index: self.name,
            user_id_index: str(self.user_id),
            icon_id_index: str(self.icon_id),
            color_1_id_index: str(self.color_1_id),
            color_2_id_index: str(self.color_2_id),
            icon_type_index: str(self.icon_type.value),
            glow_index: str(glow),
            account_id_index: str(self.account_id),
            id_index: str(self.id),
            content_index: encode_base64_string_url_safe(self.content),
            created_at_index: date_time_to_human(self.created_at),
            unread_index: unread,
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
LEVEL_DIFFICULTY_DENOMINATOR = 8
LEVEL_DIFFICULTY_NUMERATOR = 9
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
LEVEL_CREATED_AT = 28
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

UNPROCESSED_DATA = "unprocessed_data"

L = TypeVar("L", bound="LevelModel")


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
    created_at: DateTime = field(factory=utc_now)
    updated_at: DateTime = field(factory=utc_now)
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
    editor_time: Duration = field(factory=Duration)
    copies_time: Duration = field(factory=Duration)

    @classmethod
    def from_robtop(
        cls: Type[L],
        string: str,
        # indexes
        id_index: int = LEVEL_ID,
        name_index: int = LEVEL_NAME,
        description_index: int = LEVEL_DESCRIPTION,
        unprocessed_data_index: int = LEVEL_UNPROCESSED_DATA,
        version_index: int = LEVEL_VERSION,
        creator_id_index: int = LEVEL_CREATOR_ID,
        difficulty_denominator_index: int = LEVEL_DIFFICULTY_DENOMINATOR,
        difficulty_numerator_index: int = LEVEL_DIFFICULTY_NUMERATOR,
        downloads_index: int = LEVEL_DOWNLOADS,
        official_song_id_index: int = LEVEL_OFFICIAL_SONG_ID,
        game_version_index: int = LEVEL_GAME_VERSION,
        rating_index: int = LEVEL_RATING,
        length_index: int = LEVEL_LENGTH,
        demon_index: int = LEVEL_DEMON,
        stars_index: int = LEVEL_STARS,
        score_index: int = LEVEL_SCORE,
        auto_index: int = LEVEL_AUTO,
        password_data_index: int = LEVEL_PASSWORD_DATA,
        created_at_index: int = LEVEL_CREATED_AT,
        updated_at_index: int = LEVEL_UPDATED_AT,
        original_id_index: int = LEVEL_ORIGINAL_ID,
        two_player_index: int = LEVEL_TWO_PLAYER,
        custom_song_id_index: int = LEVEL_CUSTOM_SONG_ID,
        extra_string_index: int = LEVEL_EXTRA_STRING,
        coins_index: int = LEVEL_COINS,
        verified_coins_index: int = LEVEL_VERIFIED_COINS,
        requested_stars_index: int = LEVEL_REQUESTED_STARS,
        low_detail_index: int = LEVEL_LOW_DETAIL,
        timely_id_index: int = LEVEL_TIMELY_ID,
        epic_index: int = LEVEL_EPIC,
        demon_difficulty_index: int = LEVEL_DEMON_DIFFICULTY,
        object_count_index: int = LEVEL_OBJECT_COUNT,
        editor_time_index: int = LEVEL_EDITOR_TIME,
        copies_time_index: int = LEVEL_COPIES_TIME,
        # defaults
        id_default: int = DEFAULT_ID,
        name_default: str = UNNAMED,
        description_default: str = EMPTY,
        unprocessed_data_default: str = EMPTY,
        version_default: int = DEFAULT_VERSION,
        creator_id_default: int = DEFAULT_ID,
        difficulty_denominator_default: int = DEFAULT_DENOMINATOR,
        difficulty_numerator_default: int = DEFAULT_NUMERATOR,
        downloads_default: int = DEFAULT_DOWNLOADS,
        official_song_id_default: int = DEFAULT_ID,
        game_version_default: GameVersion = CURRENT_GAME_VERSION,
        rating_default: int = DEFAULT_RATING,
        length_default: LevelLength = LevelLength.DEFAULT,
        demon_default: bool = DEFAULT_DEMON,
        stars_default: int = DEFAULT_STARS,
        score_default: int = DEFAULT_SCORE,
        auto_default: bool = DEFAULT_AUTO,
        password_data_default: Optional[Password] = None,
        created_at_default: Optional[DateTime] = None,
        updated_at_default: Optional[DateTime] = None,
        original_id_default: int = DEFAULT_ID,
        two_player_default: bool = DEFAULT_TWO_PLAYER,
        custom_song_id_default: int = DEFAULT_ID,
        extra_string_default: str = EMPTY,
        coins_default: int = DEFAULT_COINS,
        verified_coins_default: bool = DEFAULT_VERIFIED_COINS,
        requested_stars_default: int = DEFAULT_STARS,
        low_detail_default: bool = DEFAULT_LOW_DETAIL,
        timely_id_default: int = DEFAULT_ID,
        epic_default: bool = DEFAULT_EPIC,
        demon_difficulty_default: DemonDifficulty = DemonDifficulty.DEFAULT,
        object_count_default: int = DEFAULT_OBJECT_COUNT,
        editor_time_default: Optional[Duration] = None,
        copies_time_default: Optional[Duration] = None,
    ) -> L:
        if password_data_default is None:
            password_data_default = Password()

        if created_at_default is None:
            created_at_default = utc_now()

        if updated_at_default is None:
            updated_at_default = utc_now()

        if editor_time_default is None:
            editor_time_default = Duration()

        if copies_time_default is None:
            copies_time_default = Duration()

        mapping = split_level(string)

        demon_difficulty_string = mapping.get(demon_difficulty_index)

        if demon_difficulty_string is None:
            demon_difficulty = demon_difficulty_default

        else:
            demon_difficulty_value = int(demon_difficulty_string)

            demon_difficulty = VALUE_TO_DEMON_DIFFICULTY.get(
                demon_difficulty_value, DemonDifficulty.HARD_DEMON
            )

        editor_time_string = mapping.get(editor_time_index)

        if editor_time_string:
            editor_time = Duration(seconds=int(editor_time_string))

        else:
            editor_time = editor_time_default

        copies_time_string = mapping.get(copies_time_index)

        if copies_time_string:
            copies_time = Duration(seconds=int(copies_time_string))

        else:
            copies_time = copies_time_default

        timely_id = parse_get_or(int, timely_id_default, mapping.get(timely_id_index))

        if timely_id:
            if timely_id // TIMELY_ID_ADD:
                timely_type = TimelyType.WEEKLY

            else:
                timely_type = TimelyType.DAILY

        else:
            timely_type = TimelyType.NOT_TIMELY

        timely_id %= TIMELY_ID_ADD

        score = parse_get_or(int, score_default, mapping.get(score_index))

        if score < 0:
            score = 0

        return cls(
            id=parse_get_or(int, id_default, mapping.get(id_index)),
            name=mapping.get(name_index, name_default),
            description=decode_base64_string_url_safe(
                mapping.get(description_index, description_default)
            ),
            unprocessed_data=mapping.get(unprocessed_data_index, unprocessed_data_default).strip(),
            version=parse_get_or(int, version_default, mapping.get(version_index)),
            creator_id=parse_get_or(int, creator_id_default, mapping.get(creator_id_index)),
            difficulty_denominator=parse_get_or(
                int,
                difficulty_denominator_default,
                mapping.get(difficulty_denominator_index),
            ),
            difficulty_numerator=parse_get_or(
                int,
                difficulty_numerator_default,
                mapping.get(difficulty_numerator_index),
            ),
            downloads=parse_get_or(int, downloads_default, mapping.get(downloads_index)),
            official_song_id=parse_get_or(
                int,
                official_song_id_default,
                mapping.get(official_song_id_index),
            ),
            game_version=parse_get_or(
                GameVersion.from_robtop,
                game_version_default,
                mapping.get(game_version_index),
            ),
            rating=parse_get_or(int, rating_default, mapping.get(rating_index)),
            length=parse_get_or(
                partial_parse_enum(int, LevelLength),
                length_default,
                mapping.get(length_index),
            ),
            demon=parse_get_or(int_bool, demon_default, mapping.get(demon_index)),
            stars=parse_get_or(int, stars_default, mapping.get(stars_index)),
            score=score,
            auto=parse_get_or(int_bool, auto_default, mapping.get(auto_index)),
            password_data=parse_get_or(
                Password.from_robtop,
                password_data_default,
                mapping.get(password_data_index),
            ),
            created_at=parse_get_or(
                date_time_from_human,
                created_at_default,
                mapping.get(created_at_index),
                ignore_errors=True,
            ),
            updated_at=parse_get_or(
                date_time_from_human,
                updated_at_default,
                mapping.get(updated_at_index),
                ignore_errors=True,
            ),
            original_id=parse_get_or(int, original_id_default, mapping.get(original_id_index)),
            two_player=parse_get_or(int_bool, two_player_default, mapping.get(two_player_index)),
            custom_song_id=parse_get_or(
                int, custom_song_id_default, mapping.get(custom_song_id_index)
            ),
            extra_string=mapping.get(extra_string_index, extra_string_default),
            coins=parse_get_or(int, coins_default, mapping.get(coins_index)),
            verified_coins=parse_get_or(
                int_bool, verified_coins_default, mapping.get(verified_coins_index)
            ),
            requested_stars=parse_get_or(
                int, requested_stars_default, mapping.get(requested_stars_index)
            ),
            low_detail=parse_get_or(int_bool, low_detail_default, mapping.get(low_detail_index)),
            timely_id=timely_id,
            timely_type=timely_type,
            epic=parse_get_or(int_bool, epic_default, mapping.get(epic_index)),
            demon_difficulty=demon_difficulty,
            object_count=parse_get_or(int, object_count_default, mapping.get(object_count_index)),
            editor_time=editor_time,
            copies_time=copies_time,
        )

    def to_robtop(
        self,
        id_index: int = LEVEL_ID,
        name_index: int = LEVEL_NAME,
        description_index: int = LEVEL_DESCRIPTION,
        unprocessed_data_index: int = LEVEL_UNPROCESSED_DATA,
        version_index: int = LEVEL_VERSION,
        creator_id_index: int = LEVEL_CREATOR_ID,
        difficulty_numerator_index: int = LEVEL_DIFFICULTY_NUMERATOR,
        difficulty_denominator_index: int = LEVEL_DIFFICULTY_DENOMINATOR,
        downloads_index: int = LEVEL_DOWNLOADS,
        official_song_id_index: int = LEVEL_OFFICIAL_SONG_ID,
        game_version_index: int = LEVEL_GAME_VERSION,
        rating_index: int = LEVEL_RATING,
        length_index: int = LEVEL_LENGTH,
        demon_index: int = LEVEL_DEMON,
        stars_index: int = LEVEL_STARS,
        score_index: int = LEVEL_SCORE,
        auto_index: int = LEVEL_AUTO,
        password_data_index: int = LEVEL_PASSWORD_DATA,
        created_at_index: int = LEVEL_CREATED_AT,
        updated_at_index: int = LEVEL_UPDATED_AT,
        original_id_index: int = LEVEL_ORIGINAL_ID,
        two_player_index: int = LEVEL_TWO_PLAYER,
        custom_song_id_index: int = LEVEL_CUSTOM_SONG_ID,
        extra_string_index: int = LEVEL_EXTRA_STRING,
        coins_index: int = LEVEL_COINS,
        verified_coins_index: int = LEVEL_VERIFIED_COINS,
        requested_stars_index: int = LEVEL_REQUESTED_STARS,
        low_detail_index: int = LEVEL_LOW_DETAIL,
        timely_id_index: int = LEVEL_TIMELY_ID,
        epic_index: int = LEVEL_EPIC,
        demon_difficulty_index: int = LEVEL_DEMON_DIFFICULTY,
        object_count_index: int = LEVEL_OBJECT_COUNT,
        editor_time_index: int = LEVEL_EDITOR_TIME,
        copies_time_index: int = LEVEL_COPIES_TIME,
    ) -> str:
        timely_id = self.timely_id

        if self.timely_type.is_weekly():
            timely_id += TIMELY_ID_ADD

        demon_difficulty_value = DEMON_DIFFICULTY_TO_VALUE.get(
            self.demon_difficulty, DemonDifficulty.DEMON.value
        )

        mapping = {
            id_index: str(self.id),
            name_index: self.name,
            description_index: encode_base64_string_url_safe(self.description),
            unprocessed_data_index: self.unprocessed_data,
            version_index: str(self.version),
            creator_id_index: str(self.creator_id),
            difficulty_denominator_index: str(self.difficulty_denominator),
            difficulty_numerator_index: str(self.difficulty_numerator),
            downloads_index: str(self.downloads),
            official_song_id_index: str(self.official_song_id),
            game_version_index: self.game_version.to_robtop(),
            rating_index: str(self.rating),
            length_index: str(self.length.value),
            demon_index: str(int(self.demon)) if self.is_demon() else EMPTY,
            stars_index: str(self.stars),
            score_index: str(self.score),
            auto_index: str(int(self.auto)) if self.is_auto() else EMPTY,
            password_data_index: self.password_data.to_robtop(),
            created_at_index: date_time_to_human(self.created_at),
            updated_at_index: date_time_to_human(self.updated_at),
            original_id_index: str(self.original_id),
            two_player_index: str(int(self.two_player)) if self.is_two_player() else EMPTY,
            custom_song_id_index: str(self.custom_song_id),
            extra_string_index: self.extra_string,
            coins_index: str(self.coins),
            verified_coins_index: str(int(self.verified_coins)),
            requested_stars_index: str(self.requested_stars),
            low_detail_index: str(int(self.low_detail)),
            timely_id_index: str(timely_id),
            epic_index: str(int(self.epic)),
            demon_difficulty_index: str(demon_difficulty_value),
            object_count_index: str(self.object_count),
            editor_time_index: str(int(self.editor_time.total_seconds())),
            copies_time_index: str(int(self.copies_time.total_seconds())),
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

    def has_verified_coins(self) -> bool:
        return self.verified_coins

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

    @property  # type: ignore
    @cache_by(UNPROCESSED_DATA)
    def processed_data(self) -> str:
        return unzip_level_string(self.unprocessed_data)

    @processed_data.setter
    def processed_data(self, data: str) -> None:
        self.unprocessed_data = zip_level_string(data)

    @property  # type: ignore
    @cache_by(UNPROCESSED_DATA)
    def data(self) -> bytes:
        return Editor.from_robtop(self.processed_data).to_bytes()

    @data.setter
    def data(self, data: bytes) -> None:
        self.processed_data = Editor.from_bytes(data).to_robtop()


LCI = TypeVar("LCI", bound="LevelCommentInnerModel")


LEVEL_COMMENT_INNER_LEVEL_ID = 1
LEVEL_COMMENT_INNER_CONTENT = 2
LEVEL_COMMENT_INNER_USER_ID = 3
LEVEL_COMMENT_INNER_RATING = 4
LEVEL_COMMENT_INNER_ID = 6
LEVEL_COMMENT_INNER_SPAM = 7
LEVEL_COMMENT_INNER_CREATED_AT = 9
LEVEL_COMMENT_INNER_RECORD = 10
LEVEL_COMMENT_INNER_ROLE_ID = 11
LEVEL_COMMENT_INNER_COLOR = 12


@define()
class LevelCommentInnerModel(Model):
    level_id: int = field(default=DEFAULT_ID)
    content: str = field(default=EMPTY)
    user_id: int = field(default=DEFAULT_ID)
    rating: int = field(default=DEFAULT_RATING)
    id: int = field(default=DEFAULT_ID)
    spam: bool = field(default=DEFAULT_SPAM)
    created_at: DateTime = field(factory=utc_now)
    record: int = field(default=DEFAULT_RECORD)
    role_id: int = field(default=DEFAULT_ID)
    color: Color = field(factory=Color.default)

    @classmethod
    def from_robtop(
        cls: Type[LCI],
        string: str,
        # indexes
        level_id_index: int = LEVEL_COMMENT_INNER_LEVEL_ID,
        content_index: int = LEVEL_COMMENT_INNER_CONTENT,
        user_id_index: int = LEVEL_COMMENT_INNER_USER_ID,
        rating_index: int = LEVEL_COMMENT_INNER_RATING,
        id_index: int = LEVEL_COMMENT_INNER_ID,
        spam_index: int = LEVEL_COMMENT_INNER_SPAM,
        created_at_index: int = LEVEL_COMMENT_INNER_CREATED_AT,
        record_index: int = LEVEL_COMMENT_INNER_RECORD,
        role_id_index: int = LEVEL_COMMENT_INNER_ROLE_ID,
        color_index: int = LEVEL_COMMENT_INNER_COLOR,
        # defaults
        level_id_default: int = DEFAULT_ID,
        content_default: str = EMPTY,
        user_id_default: int = DEFAULT_ID,
        rating_default: int = DEFAULT_RATING,
        id_default: int = DEFAULT_ID,
        spam_default: bool = DEFAULT_SPAM,
        created_at_default: Optional[DateTime] = None,
        record_default: int = DEFAULT_RECORD,
        role_id_default: int = DEFAULT_ID,
        color_default: Optional[Color] = None,
    ) -> LCI:
        if created_at_default is None:
            created_at_default = utc_now()

        if color_default is None:
            color_default = Color.default()

        mapping = split_level_comment_inner(string)

        return cls(
            level_id=parse_get_or(
                int,
                level_id_default,
                mapping.get(level_id_index),
            ),
            content=decode_base64_string_url_safe(mapping.get(content_index, content_default)),
            user_id=parse_get_or(
                int,
                user_id_default,
                mapping.get(user_id_index),
            ),
            rating=parse_get_or(
                int,
                rating_default,
                mapping.get(rating_index),
            ),
            id=parse_get_or(int, id_default, mapping.get(id_index)),
            spam=parse_get_or(
                int_bool,
                spam_default,
                mapping.get(spam_index),
            ),
            created_at=parse_get_or(
                date_time_from_human,
                created_at_default,
                mapping.get(created_at_index),
                ignore_errors=True,
            ),
            record=parse_get_or(
                int,
                record_default,
                mapping.get(record_index),
            ),
            role_id=parse_get_or(
                int,
                role_id_default,
                mapping.get(role_id_index),
            ),
            color=parse_get_or(
                Color.from_robtop,
                color_default,
                mapping.get(color_index),
            ),
        )

    def to_robtop(
        self,
        level_id_index: int = LEVEL_COMMENT_INNER_LEVEL_ID,
        content_index: int = LEVEL_COMMENT_INNER_CONTENT,
        user_id_index: int = LEVEL_COMMENT_INNER_USER_ID,
        rating_index: int = LEVEL_COMMENT_INNER_RATING,
        id_index: int = LEVEL_COMMENT_INNER_ID,
        spam_index: int = LEVEL_COMMENT_INNER_SPAM,
        created_at_index: int = LEVEL_COMMENT_INNER_CREATED_AT,
        record_index: int = LEVEL_COMMENT_INNER_RECORD,
        role_id_index: int = LEVEL_COMMENT_INNER_ROLE_ID,
        color_index: int = LEVEL_COMMENT_INNER_COLOR,
    ) -> str:
        mapping = {
            level_id_index: str(self.level_id),
            content_index: encode_base64_string_url_safe(self.content),
            user_id_index: str(self.user_id),
            rating_index: str(self.rating),
            id_index: str(self.id),
            spam_index: str(int(self.spam)),
            created_at_index: date_time_to_human(self.created_at),
            record_index: str(self.record),
            role_id_index: str(self.role_id),
            color_index: self.color.to_robtop(),
        }

        return concat_level_comment_inner(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_COMMENT_INNER_SEPARATOR in string

    def is_spam(self) -> bool:
        return self.spam


LEVEL_COMMENT_USER_NAME = 1
LEVEL_COMMENT_USER_ICON_ID = 9
LEVEL_COMMENT_USER_COLOR_1_ID = 10
LEVEL_COMMENT_USER_COLOR_2_ID = 11
LEVEL_COMMENT_USER_ICON_TYPE = 14
LEVEL_COMMENT_USER_GLOW = 15
LEVEL_COMMENT_USER_ACCOUNT_ID = 16


LCU = TypeVar("LCU", bound="LevelCommentUserModel")


@define()
class LevelCommentUserModel(Model):
    name: str = UNKNOWN
    icon_id: int = DEFAULT_ICON_ID
    color_1_id: int = DEFAULT_COLOR_1_ID
    color_2_id: int = DEFAULT_COLOR_2_ID
    icon_type: IconType = IconType.DEFAULT
    glow: bool = DEFAULT_GLOW
    account_id: int = DEFAULT_ID

    @classmethod
    def from_robtop(
        cls: Type[LCU],
        string: str,
        # indexes
        name_index: int = LEVEL_COMMENT_USER_NAME,
        icon_id_index: int = LEVEL_COMMENT_USER_ICON_ID,
        color_1_id_index: int = LEVEL_COMMENT_USER_COLOR_1_ID,
        color_2_id_index: int = LEVEL_COMMENT_USER_COLOR_2_ID,
        icon_type_index: int = LEVEL_COMMENT_USER_ICON_TYPE,
        glow_index: int = LEVEL_COMMENT_USER_GLOW,
        account_id_index: int = LEVEL_COMMENT_USER_ACCOUNT_ID,
        # defaults
        name_default: str = UNKNOWN,
        icon_id_default: int = DEFAULT_ICON_ID,
        color_1_id_default: int = DEFAULT_COLOR_1_ID,
        color_2_id_default: int = DEFAULT_COLOR_2_ID,
        icon_type_default: IconType = IconType.DEFAULT,
        glow_default: bool = DEFAULT_GLOW,
        account_id_default: int = DEFAULT_ID,
    ) -> LCU:
        mapping = split_level_comment_user(string)

        return cls(
            name=mapping.get(name_index, name_default),
            icon_id=parse_get_or(
                int,
                icon_id_default,
                mapping.get(icon_id_index),
            ),
            color_1_id=parse_get_or(
                int,
                color_1_id_default,
                mapping.get(color_1_id_index),
            ),
            color_2_id=parse_get_or(
                int,
                color_2_id_default,
                mapping.get(color_2_id_index),
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                icon_type_default,
                mapping.get(icon_type_index),
            ),
            glow=parse_get_or(
                int_bool,
                glow_default,
                mapping.get(glow_index),
            ),
            account_id=parse_get_or(
                int,
                account_id_default,
                mapping.get(account_id_index),
            ),
        )

    def to_robtop(
        self,
        name_index: int = LEVEL_COMMENT_USER_NAME,
        icon_id_index: int = LEVEL_COMMENT_USER_ICON_ID,
        color_1_id_index: int = LEVEL_COMMENT_USER_COLOR_1_ID,
        color_2_id_index: int = LEVEL_COMMENT_USER_COLOR_2_ID,
        icon_type_index: int = LEVEL_COMMENT_USER_ICON_TYPE,
        glow_index: int = LEVEL_COMMENT_USER_GLOW,
        account_id_index: int = LEVEL_COMMENT_USER_ACCOUNT_ID,
    ) -> str:
        glow = self.glow

        glow += glow  # type: ignore

        mapping = {
            name_index: self.name,
            icon_id_index: str(self.icon_id),
            color_1_id_index: str(self.color_1_id),
            color_2_id_index: str(self.color_2_id),
            icon_type_index: str(self.icon_type.value),
            glow_index: str(glow),
            account_id_index: str(self.account_id),
        }

        return concat_level_comment_user(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_COMMENT_USER_SEPARATOR in string


LC = TypeVar("LC", bound="LevelCommentModel")


@define()
class LevelCommentModel(Model):
    inner: LevelCommentInnerModel = field(factory=LevelCommentInnerModel)
    user: LevelCommentUserModel = field(factory=LevelCommentUserModel)

    @classmethod
    def from_robtop(cls: Type[LC], string: str) -> LC:
        inner_string, user_string = split_level_comment(string)

        inner = LevelCommentInnerModel.from_robtop(inner_string)
        user = LevelCommentUserModel.from_robtop(user_string)

        return cls(inner=inner, user=user)

    def to_robtop(self) -> str:
        values = (self.inner.to_robtop(), self.user.to_robtop())

        return concat_level_comment(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_COMMENT_SEPARATOR in string


UC = TypeVar("UC", bound="UserCommentModel")


USER_COMMENT_CONTENT = 2
USER_COMMENT_RATING = 4
USER_COMMENT_ID = 6
USER_COMMENT_CREATED_AT = 9


@define()
class UserCommentModel(Model):
    content: str = field(default=EMPTY)
    rating: int = field(default=DEFAULT_RATING)
    id: int = field(default=DEFAULT_ID)
    created_at: DateTime = field(factory=utc_now)

    @classmethod
    def from_robtop(
        cls: Type[UC],
        string: str,
        # indexes
        content_index: int = USER_COMMENT_CONTENT,
        rating_index: int = USER_COMMENT_RATING,
        id_index: int = USER_COMMENT_ID,
        created_at_index: int = USER_COMMENT_CREATED_AT,
        # defaults
        content_default: str = EMPTY,
        rating_default: int = DEFAULT_RATING,
        id_default: int = DEFAULT_ID,
        created_at_default: Optional[DateTime] = None,
    ) -> UC:
        if created_at_default is None:
            created_at_default = utc_now()

        mapping = split_user_comment(string)

        return cls(
            content=decode_base64_string_url_safe(mapping.get(content_index, content_default)),
            rating=parse_get_or(int, rating_default, mapping.get(rating_index)),
            id=parse_get_or(int, id_default, mapping.get(id_index)),
            created_at=parse_get_or(
                date_time_from_human,
                created_at_default,
                mapping.get(created_at_index),
                ignore_errors=True,
            ),
        )

    def to_robtop(
        self,
        content_index: int = USER_COMMENT_CONTENT,
        rating_index: int = USER_COMMENT_RATING,
        id_index: int = USER_COMMENT_ID,
        created_at_index: int = USER_COMMENT_CREATED_AT,
    ) -> str:
        mapping = {
            content_index: decode_base64_string_url_safe(self.content),
            rating_index: str(self.rating),
            id_index: str(self.id),
            created_at_index: date_time_to_human(self.created_at),
        }

        return concat_user_comment(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return USER_COMMENT_SEPARATOR in string


LEVEL_LEADERBOARD_USER_NAME = 1
LEVEL_LEADERBOARD_USER_ID = 2
LEVEL_LEADERBOARD_USER_RECORD = 3
LEVEL_LEADERBOARD_USER_PLACE = 6
LEVEL_LEADERBOARD_USER_ICON_ID = 9
LEVEL_LEADERBOARD_USER_COLOR_1_ID = 10
LEVEL_LEADERBOARD_USER_COLOR_2_ID = 11
LEVEL_LEADERBOARD_USER_COINS = 13
LEVEL_LEADERBOARD_USER_ICON_TYPE = 14
LEVEL_LEADERBOARD_USER_GLOW = 15
LEVEL_LEADERBOARD_USER_ACCOUNT_ID = 16
LEVEL_LEADERBOARD_USER_RECORDED_AT = 42

LLU = TypeVar("LLU", bound="LevelLeaderboardUserModel")


@define()
class LevelLeaderboardUserModel(Model):
    name: str = field(default=UNKNOWN)
    id: int = field(default=DEFAULT_ID)
    record: int = field(default=DEFAULT_RECORD)
    place: int = field(default=DEFAULT_PLACE)
    icon_id: int = field(default=DEFAULT_ICON_ID)
    color_1_id: int = field(default=DEFAULT_COLOR_1_ID)
    color_2_id: int = field(default=DEFAULT_COLOR_2_ID)
    coins: int = field(default=DEFAULT_COINS)
    icon_type: IconType = field(default=IconType.DEFAULT)
    glow: bool = field(default=DEFAULT_GLOW)
    account_id: int = field(default=DEFAULT_ID)
    recorded_at: DateTime = field(factory=utc_now)

    @classmethod
    def from_robtop(
        cls: Type[LLU],
        string: str,
        # indexes
        name_index: int = LEVEL_LEADERBOARD_USER_NAME,
        id_index: int = LEVEL_LEADERBOARD_USER_ID,
        record_index: int = LEVEL_LEADERBOARD_USER_RECORD,
        place_index: int = LEVEL_LEADERBOARD_USER_PLACE,
        icon_id_index: int = LEVEL_LEADERBOARD_USER_ICON_ID,
        color_1_id_index: int = LEVEL_LEADERBOARD_USER_COLOR_1_ID,
        color_2_id_index: int = LEVEL_LEADERBOARD_USER_COLOR_2_ID,
        coins_index: int = LEVEL_LEADERBOARD_USER_COINS,
        icon_type_index: int = LEVEL_LEADERBOARD_USER_ICON_TYPE,
        glow_index: int = LEVEL_LEADERBOARD_USER_GLOW,
        recorded_at_index: int = LEVEL_LEADERBOARD_USER_RECORDED_AT,
        # defaults
        name_default: str = UNKNOWN,
        id_default: int = DEFAULT_ID,
        record_default: int = DEFAULT_RECORD,
        place_default: int = DEFAULT_PLACE,
        icon_id_default: int = DEFAULT_ICON_ID,
        color_1_id_default: int = DEFAULT_COLOR_1_ID,
        color_2_id_default: int = DEFAULT_COLOR_2_ID,
        coins_default: int = DEFAULT_COINS,
        icon_type_default: IconType = IconType.DEFAULT,
        glow_default: bool = DEFAULT_GLOW,
        recorded_at_default: Optional[DateTime] = None,
    ) -> LLU:
        if recorded_at_default is None:
            recorded_at_default = utc_now()

        mapping = split_level_leaderboard_user(string)

        return cls(
            name=mapping.get(name_index, name_default),
            id=parse_get_or(int, id_default, mapping.get(id_index)),
            record=parse_get_or(int, record_default, mapping.get(record_index)),
            place=parse_get_or(int, place_default, mapping.get(place_index)),
            icon_id=parse_get_or(int, icon_id_default, mapping.get(icon_id_index)),
            color_1_id=parse_get_or(int, color_1_id_default, mapping.get(color_1_id_index)),
            color_2_id=parse_get_or(int, color_2_id_default, mapping.get(color_2_id_index)),
            coins=parse_get_or(int, coins_default, mapping.get(coins_index)),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType), icon_type_default, mapping.get(icon_type_index)
            ),
            glow=parse_get_or(int_bool, glow_default, mapping.get(glow_index)),
            recorded_at=parse_get_or(
                date_time_from_human, recorded_at_default, mapping.get(recorded_at_index)
            ),
        )

    def to_robtop(
        self,
        name_index: int = LEVEL_LEADERBOARD_USER_NAME,
        id_index: int = LEVEL_LEADERBOARD_USER_ID,
        record_index: int = LEVEL_LEADERBOARD_USER_RECORD,
        place_index: int = LEVEL_LEADERBOARD_USER_PLACE,
        icon_id_index: int = LEVEL_LEADERBOARD_USER_ICON_ID,
        color_1_id_index: int = LEVEL_LEADERBOARD_USER_COLOR_1_ID,
        color_2_id_index: int = LEVEL_LEADERBOARD_USER_COLOR_2_ID,
        coins_index: int = LEVEL_LEADERBOARD_USER_COINS,
        icon_type_index: int = LEVEL_LEADERBOARD_USER_ICON_TYPE,
        glow_index: int = LEVEL_LEADERBOARD_USER_GLOW,
        account_id_index: int = LEVEL_LEADERBOARD_USER_ACCOUNT_ID,
        recorded_at_index: int = LEVEL_LEADERBOARD_USER_RECORDED_AT,
    ) -> str:
        glow = self.glow

        glow += glow  # type: ignore

        mapping = {
            name_index: self.name,
            id_index: str(self.id),
            record_index: str(self.record),
            place_index: str(self.place),
            icon_id_index: str(self.icon_id),
            color_1_id_index: str(self.color_1_id),
            color_2_id_index: str(self.color_2_id),
            coins_index: str(self.coins),
            icon_type_index: str(self.icon_type.value),
            glow_index: str(glow),
            account_id_index: str(self.account_id),
            recorded_at_index: date_time_to_human(self.recorded_at),
        }

        return concat_level_leaderboard_user(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_LEADERBOARD_USER_SEPARATOR in string


LLR = TypeVar("LLR", bound="LevelLeaderboardResponseModel")


@define()
class LevelLeaderboardResponseModel(Model):
    users: List[LevelLeaderboardUserModel] = field(factory=list)

    @classmethod
    def from_robtop(cls: Type[LLR], string: str) -> LLR:
        users = [
            LevelLeaderboardUserModel.from_robtop(string)
            for string in split_level_leaderboard_response_users(string)
        ]

        return cls(users=users)

    def to_robtop(self) -> str:
        return concat_level_leaderboard_response_users(user.to_robtop() for user in self.users)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_LEADERBOARD_RESPONSE_USERS_SEPARATOR in string


LCR = TypeVar("LCR", bound="LevelCommentsResponseModel")


@define()
class LevelCommentsResponseModel(Model):
    comments: List[LevelCommentModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[LCR], string: str) -> LCR:
        comments_string, page_string = split_level_comments_response(string)

        comments = [
            LevelCommentModel.from_robtop(string)
            for string in split_level_comments_response_comments(comments_string)
        ]

        page = PageModel.from_robtop(page_string)

        return cls(comments=comments, page=page)

    def to_robtop(self) -> str:
        values = (
            concat_level_comments_response_comments(
                comment.to_robtop() for comment in self.comments
            ),
            self.page.to_robtop(),
        )

        return concat_level_comments_response(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_COMMENTS_RESPONSE_SEPARATOR in string


UCR = TypeVar("UCR", bound="UserCommentsResponseModel")


@define()
class UserCommentsResponseModel(Model):
    comments: List[UserCommentModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[UCR], string: str) -> UCR:
        comments_string, page_string = split_user_comments_response(string)

        comments = [
            UserCommentModel.from_robtop(string)
            for string in split_user_comments_response_comments(comments_string)
        ]

        page = PageModel.from_robtop(page_string)

        return cls(comments=comments, page=page)

    def to_robtop(self) -> str:
        values = (
            concat_user_comments_response_comments(
                comment.to_robtop() for comment in self.comments
            ),
            self.page.to_robtop(),
        )

        return concat_user_comments_response(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return USER_COMMENTS_RESPONSE_SEPARATOR in string


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
        return sha1_string_with_salt(
            generate_level_seed(self.level.to_robtop(), SMART_HASH_COUNT), Salt.LEVEL
        )

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
        creator = self.creator

        values: DynamicTuple[str]

        if creator is None:
            values = (self.level.to_robtop(), self.smart_hash, self.hash)

        else:
            values = (self.level.to_robtop(), self.smart_hash, self.hash, creator.to_robtop())

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
        (
            levels_string,
            creators_string,
            songs_string,
            page_string,
            hash,
        ) = split_search_levels_response(string)

        levels = [
            LevelModel.from_robtop(string)
            for string in split_search_levels_response_levels(levels_string)
        ]

        creators = [
            CreatorModel.from_robtop(string)
            for string in split_search_levels_response_creators(creators_string)
        ]

        songs = [
            SongModel.from_robtop(string)
            for string in split_search_levels_response_songs(songs_string)
        ]

        page = PageModel.from_robtop(page_string)

        return cls(levels=levels, creators=creators, songs=songs, page=page, hash=hash)

    def to_robtop(self) -> str:
        values = (
            concat_search_levels_response_levels(level.to_robtop() for level in self.levels),
            concat_search_levels_response_creators(
                creator.to_robtop() for creator in self.creators
            ),
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


LBR = TypeVar("LBR", bound="LeaderboardResponseModel")


@define()
class LeaderboardResponseModel(Model):
    users: List[LeaderboardUserModel] = field(factory=list)

    @classmethod
    def from_robtop(cls: Type[LBR], string: str) -> LBR:
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
    timeout: Duration = field(factory=Duration)
    reason: str = field(default=EMPTY)

    @classmethod
    def from_robtop(cls: Type[B], string: str) -> B:
        string, timeout, reason = split_comment_banned(string)

        return cls(string, Duration(seconds=int(timeout)), reason)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return COMMENT_BANNED_SEPARATOR in string

    def to_robtop(self) -> str:
        values = (self.string, str(int(self.timeout.total_seconds())), self.reason)

        return concat_comment_banned(values)
