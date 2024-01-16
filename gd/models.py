from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
    runtime_checkable,
)
from urllib.parse import quote, unquote

from attrs import define, field
from funcs.primitives import decrement, increment
from iters.iters import iter
from pendulum import DateTime, Duration, duration
from yarl import URL

from gd.api.editor import Editor
from gd.capacity import Capacity
from gd.color import Color
from gd.constants import (
    CHESTS_SLICE,
    DEFAULT_ACTIVE,
    DEFAULT_AMOUNT,
    DEFAULT_ARTIST_VERIFIED,
    DEFAULT_AUTO,
    DEFAULT_CHEST_COUNT,
    DEFAULT_COINS,
    DEFAULT_COLOR_1_ID,
    DEFAULT_COLOR_2_ID,
    DEFAULT_COLOR_3_ID,
    DEFAULT_CONTENT_PRESENT,
    DEFAULT_COUNT,
    DEFAULT_CREATOR_POINTS,
    DEFAULT_DEMON,
    DEFAULT_DEMONS,
    DEFAULT_DENOMINATOR,
    DEFAULT_DIAMONDS,
    DEFAULT_DOWNLOADS,
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    DEFAULT_GLOW,
    DEFAULT_ICON_ID,
    DEFAULT_ID,
    DEFAULT_KEYS,
    DEFAULT_LOW_DETAIL,
    DEFAULT_MOONS,
    DEFAULT_NEW,
    DEFAULT_NUMERATOR,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_ORBS,
    DEFAULT_PLACE,
    DEFAULT_PLATFORMER,
    DEFAULT_RANK,
    DEFAULT_RATING,
    DEFAULT_READ,
    DEFAULT_RECORD,
    DEFAULT_REWARD,
    DEFAULT_SCORE,
    DEFAULT_SECRET_COINS,
    DEFAULT_SENT,
    DEFAULT_SIZE,
    DEFAULT_SPAM,
    DEFAULT_STARS,
    DEFAULT_TIME_STEPS,
    DEFAULT_TWO_PLAYER,
    DEFAULT_UNREAD,
    DEFAULT_USER_COINS,
    DEFAULT_VERIFIED_COINS,
    DEFAULT_VERSION,
    EMPTY,
    QUESTS_SLICE,
    WEEKLY_ID_ADD,
)
from gd.converter import dump_url
from gd.date_time import (
    date_time_to_human,
    duration_from_seconds,
    option_date_time_from_human,
    utc_now,
)
from gd.decorators import cache_by
from gd.demon_info import DemonInfo
from gd.difficulty_parameters import DifficultyParameters
from gd.either_record import EitherRecord
from gd.either_reward import EitherReward
from gd.encoding import (
    decode_base64_string_url_safe,
    decode_robtop_string_with,
    encode_base64_string_url_safe,
    encode_robtop_string_with,
    generate_level_seed,
    generate_random_string,
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
    LevelLength,
    MessageState,
    QuestType,
    RewardType,
    Salt,
    ShardType,
    SpecialRateType,
    TimelyType,
)
from gd.models_constants import (
    ARTIST_SEPARATOR,
    ARTISTS_RESPONSE_SEPARATOR,
    CHEST_SEPARATOR,
    CHESTS_INNER_SEPARATOR,
    CHESTS_RESPONSE_SEPARATOR,
    COMMENT_BANNED_SEPARATOR,
    CREATOR_SEPARATOR,
    FRIEND_REQUEST_SEPARATOR,
    GAUNTLET_SEPARATOR,
    GAUNTLETS_RESPONSE_SEPARATOR,
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
    MAP_PACK_SEPARATOR,
    MAP_PACKS_RESPONSE_SEPARATOR,
    MESSAGE_SEPARATOR,
    MESSAGES_RESPONSE_SEPARATOR,
    PAGE_SEPARATOR,
    PROFILE_SEPARATOR,
    QUEST_SEPARATOR,
    QUESTS_INNER_SEPARATOR,
    QUESTS_RESPONSE_SEPARATOR,
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
    bool_str,
    concat_artist,
    concat_artists_response,
    concat_artists_response_artists,
    concat_chest,
    concat_chests_inner,
    concat_chests_response,
    concat_comment_banned,
    concat_creator,
    concat_friend_request,
    concat_friend_requests_response,
    concat_friend_requests_response_friend_requests,
    concat_gauntlet,
    concat_gauntlets_response,
    concat_gauntlets_response_gauntlets,
    concat_leaderboard_response_users,
    concat_leaderboard_user,
    concat_level,
    concat_level_comment,
    concat_level_comment_inner,
    concat_level_comment_user,
    concat_level_comments_response,
    concat_level_comments_response_comments,
    concat_level_ids,
    concat_level_leaderboard_response_users,
    concat_level_leaderboard_user,
    concat_level_response,
    concat_login,
    concat_map_pack,
    concat_map_packs_response,
    concat_map_packs_response_map_packs,
    concat_message,
    concat_messages_response,
    concat_messages_response_messages,
    concat_page,
    concat_profile,
    concat_quest,
    concat_quests_inner,
    concat_quests_response,
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
    option_int,
    split_artist,
    split_artists_response,
    split_artists_response_artists,
    split_chest,
    split_chests_inner,
    split_chests_response,
    split_comment_banned,
    split_creator,
    split_friend_request,
    split_friend_requests_response,
    split_friend_requests_response_friend_requests,
    split_gauntlet,
    split_gauntlets_response,
    split_gauntlets_response_gauntlets,
    split_leaderboard_response_users,
    split_leaderboard_user,
    split_level,
    split_level_comment,
    split_level_comment_inner,
    split_level_comment_user,
    split_level_comments_response,
    split_level_comments_response_comments,
    split_level_ids,
    split_level_leaderboard_response_users,
    split_level_leaderboard_user,
    split_level_response,
    split_login,
    split_map_pack,
    split_map_packs_response,
    split_map_packs_response_map_packs,
    split_message,
    split_messages_response,
    split_messages_response_messages,
    split_page,
    split_profile,
    split_quest,
    split_quests_inner,
    split_quests_response,
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
from gd.robtop_view import RobTopView
from gd.string_utils import concat_empty
from gd.versions import CURRENT_GAME_VERSION, GameVersion

if TYPE_CHECKING:
    from typing_aliases import DynamicTuple
    from typing_extensions import Self

__all__ = (
    "Model",
    "ArtistModel",
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

FIRST = 0
LAST = ~0

T = TypeVar("T")


def first(sequence: Sequence[T]) -> T:
    return sequence[FIRST]


def last(sequence: Sequence[T]) -> T:
    return sequence[LAST]


@runtime_checkable
class Model(RobTop, Protocol):
    """Represents various models."""


SONG_ID = 1
SONG_NAME = 2
SONG_ARTIST_ID = 3
SONG_ARTIST_NAME = 4
SONG_SIZE = 5
SONG_YOUTUBE_VIDEO_ID = 6
SONG_YOUTUBE_CHANNEL_ID = 7
SONG_ARTIST_VERIFIED = 8
SONG_URL = 10


@define()
class SongModel(Model):
    id: int = DEFAULT_ID
    name: str = EMPTY
    artist_id: int = DEFAULT_ID
    artist_name: str = EMPTY
    size: float = DEFAULT_SIZE
    youtube_video_id: str = EMPTY
    youtube_channel_id: str = EMPTY
    artist_verified: bool = DEFAULT_ARTIST_VERIFIED
    url: Optional[URL] = None

    @classmethod
    def from_robtop(
        cls, string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
    ) -> Self:
        mapping = split_song(string)

        view = RobTopView(mapping)

        id = view.get_option(SONG_ID).map(int).unwrap_or(DEFAULT_ID)

        name = view.get_option(SONG_NAME).unwrap_or(EMPTY)

        artist_name = view.get_option(SONG_ARTIST_NAME).unwrap_or(EMPTY)

        artist_id = view.get_option(SONG_ARTIST_ID).map(int).unwrap_or(DEFAULT_ID)

        size = view.get_option(SONG_SIZE).map(float).unwrap_or(DEFAULT_SIZE)

        youtube_video_id = view.get_option(SONG_YOUTUBE_VIDEO_ID).unwrap_or(EMPTY)
        youtube_channel_id = view.get_option(SONG_YOUTUBE_CHANNEL_ID).unwrap_or(EMPTY)

        artist_verified = (
            view.get_option(SONG_ARTIST_VERIFIED).map(int_bool).unwrap_or(DEFAULT_ARTIST_VERIFIED)
        )

        url = view.get_option(SONG_URL).filter(bool).map(unquote).map(URL).extract()

        return cls(
            id=id,
            name=name,
            artist_name=artist_name,
            artist_id=artist_id,
            size=size,
            youtube_video_id=youtube_video_id,
            youtube_channel_id=youtube_channel_id,
            artist_verified=artist_verified,
            url=url,
        )

    def to_robtop(self) -> str:
        url = self.url

        mapping = {
            SONG_ID: str(self.id),
            SONG_NAME: self.name,
            SONG_ARTIST_NAME: self.artist_name,
            SONG_ARTIST_ID: str(self.artist_id),
            SONG_SIZE: float_str(self.size),
            SONG_YOUTUBE_VIDEO_ID: self.youtube_video_id,
            SONG_YOUTUBE_CHANNEL_ID: self.youtube_channel_id,
            SONG_ARTIST_VERIFIED: bool_str(self.is_artist_verified()),
            SONG_URL: EMPTY if url is None else quote(dump_url(url)),
        }

        return concat_song(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return SONG_SEPARATOR in string

    def is_artist_verified(self) -> bool:
        return self.artist_verified


@define()
class LoginModel(Model):
    account_id: int = DEFAULT_ID
    id: int = DEFAULT_ID

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        account_id, id = iter(split_login(string)).map(int).tuple()

        return cls(account_id=account_id, id=id)

    def to_robtop(self) -> str:
        return iter.of(str(self.account_id), str(self.id)).collect(concat_login)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LOGIN_SEPARATOR in string


@define()
class CreatorModel(Model):
    id: int = DEFAULT_ID
    name: str = EMPTY
    account_id: int = DEFAULT_ID

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        id_string, name, account_id_string = split_creator(string)

        id = int(id_string)

        account_id = int(account_id_string)

        return cls(id=id, name=name, account_id=account_id)

    def to_robtop(self) -> str:
        return iter.of(str(self.id), self.name, str(self.account_id)).collect(concat_creator)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return CREATOR_SEPARATOR in string


DEFAULT_START = 0
DEFAULT_STOP = 0


@define()
class PageModel(Model):
    total: Optional[int] = None
    start: int = DEFAULT_START
    stop: int = DEFAULT_STOP

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        total_option, start_option, stop_option = iter(split_page(string)).map(option_int).tuple()

        total = total_option.extract()
        start = start_option.unwrap_or(DEFAULT_START)
        stop = stop_option.unwrap_or(DEFAULT_STOP)

        return cls(total=total, start=start, stop=stop)

    def to_robtop(self) -> str:
        total = self.total
        start = self.start
        stop = self.stop

        if total is None:
            return iter.of(EMPTY, str(start), str(stop)).collect(concat_page)

        return iter.of(str(total), str(start), str(stop)).collect(concat_page)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return PAGE_SEPARATOR in string


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
SEARCH_USER_DIAMONDS = 46
SEARCH_USER_MOONS = 52


@define()
class SearchUserModel(Model):
    name: str = EMPTY
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
    diamonds: int = DEFAULT_DIAMONDS
    moons: int = DEFAULT_MOONS

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_search_user(string)

        view = RobTopView(mapping)

        name = view.get_option(SEARCH_USER_NAME).unwrap_or(EMPTY)

        id = view.get_option(SEARCH_USER_ID).map(int).unwrap_or(DEFAULT_ID)

        stars = view.get_option(SEARCH_USER_STARS).map(int).unwrap_or(DEFAULT_STARS)

        demons = view.get_option(SEARCH_USER_DEMONS).map(int).unwrap_or(DEFAULT_DEMONS)

        rank = view.get_option(SEARCH_USER_RANK).filter(bool).map(int).unwrap_or(DEFAULT_RANK)

        creator_points = (
            view.get_option(SEARCH_USER_CREATOR_POINTS).map(int).unwrap_or(DEFAULT_CREATOR_POINTS)
        )

        icon_id = view.get_option(SEARCH_USER_ICON_ID).map(int).unwrap_or(DEFAULT_ID)

        color_1_id = view.get_option(SEARCH_USER_COLOR_1_ID).map(int).unwrap_or(DEFAULT_COLOR_1_ID)
        color_2_id = view.get_option(SEARCH_USER_COLOR_2_ID).map(int).unwrap_or(DEFAULT_COLOR_2_ID)

        secret_coins = (
            view.get_option(SEARCH_USER_SECRET_COINS).map(int).unwrap_or(DEFAULT_SECRET_COINS)
        )

        icon_type = (
            view.get_option(SEARCH_USER_ICON_TYPE)
            .map(int)
            .map(IconType)
            .unwrap_or(IconType.DEFAULT)
        )

        glow = view.get_option(SEARCH_USER_GLOW).map(int_bool).unwrap_or(DEFAULT_GLOW)

        account_id = view.get_option(SEARCH_USER_ACCOUNT_ID).map(int).unwrap_or(DEFAULT_ID)

        user_coins = view.get_option(SEARCH_USER_USER_COINS).map(int).unwrap_or(DEFAULT_USER_COINS)

        diamonds = view.get_option(SEARCH_USER_DIAMONDS).map(int).unwrap_or(DEFAULT_DIAMONDS)

        moons = view.get_option(SEARCH_USER_MOONS).map(int).unwrap_or(DEFAULT_MOONS)

        return cls(
            name=name,
            id=id,
            stars=stars,
            demons=demons,
            rank=rank,
            creator_points=creator_points,
            icon_id=icon_id,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            secret_coins=secret_coins,
            icon_type=icon_type,
            glow=glow,
            account_id=account_id,
            user_coins=user_coins,
            diamonds=diamonds,
            moons=moons,
        )

    def to_robtop(self) -> str:
        glow = self.has_glow()

        glow += glow  # type: ignore

        mapping = {
            SEARCH_USER_NAME: self.name,
            SEARCH_USER_ID: str(self.id),
            SEARCH_USER_STARS: str(self.stars),
            SEARCH_USER_DEMONS: str(self.demons),
            SEARCH_USER_RANK: str(self.rank),
            SEARCH_USER_CREATOR_POINTS: str(self.creator_points),
            SEARCH_USER_ICON_ID: str(self.icon_id),
            SEARCH_USER_COLOR_1_ID: str(self.color_1_id),
            SEARCH_USER_COLOR_2_ID: str(self.color_2_id),
            SEARCH_USER_SECRET_COINS: str(self.secret_coins),
            SEARCH_USER_ICON_TYPE: str(self.icon_type.value),
            SEARCH_USER_GLOW: str(glow),
            SEARCH_USER_ACCOUNT_ID: str(self.account_id),
            SEARCH_USER_USER_COINS: str(self.user_coins),
            SEARCH_USER_DIAMONDS: str(self.diamonds),
            SEARCH_USER_MOONS: str(self.moons),
        }

        return concat_search_user(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return SEARCH_USER_SEPARATOR in string

    def has_glow(self) -> bool:
        return self.glow


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
PROFILE_X = 44
PROFILE_TWITCH = 45
PROFILE_DIAMONDS = 46
PROFILE_EXPLOSION_ID = 48
PROFILE_ROLE_ID = 49
PROFILE_COMMENT_STATE = 50
PROFILE_COLOR_3_ID = 51
PROFILE_MOONS = 52
PROFILE_SWING_ID = 53
PROFILE_JETPACK_ID = 54
PROFILE_DEMON_INFO = 55


@define()
class ProfileModel(Model):
    name: str = field(default=EMPTY)
    id: int = field(default=DEFAULT_ID)
    stars: int = field(default=DEFAULT_STARS)
    demons: int = field(default=DEFAULT_DEMONS)
    creator_points: int = field(default=DEFAULT_CREATOR_POINTS)
    color_1_id: int = field(default=DEFAULT_COLOR_1_ID)
    color_2_id: int = field(default=DEFAULT_COLOR_2_ID)
    secret_coins: int = field(default=DEFAULT_SECRET_COINS)
    account_id: int = field(default=DEFAULT_ID)
    user_coins: int = field(default=DEFAULT_USER_COINS)
    message_state: MessageState = field(default=MessageState.DEFAULT)
    friend_request_state: FriendRequestState = field(default=FriendRequestState.DEFAULT)
    youtube: Optional[str] = field(default=None)
    cube_id: int = field(default=DEFAULT_ICON_ID)
    ship_id: int = field(default=DEFAULT_ICON_ID)
    ball_id: int = field(default=DEFAULT_ICON_ID)
    ufo_id: int = field(default=DEFAULT_ICON_ID)
    wave_id: int = field(default=DEFAULT_ICON_ID)
    robot_id: int = field(default=DEFAULT_ICON_ID)
    glow: bool = field(default=DEFAULT_GLOW)
    active: bool = field(default=DEFAULT_ACTIVE)
    rank: int = field(default=DEFAULT_RANK)
    friend_state: FriendState = field(default=FriendState.DEFAULT)
    new_messages: int = field(default=DEFAULT_NEW)
    new_friend_requests: int = field(default=DEFAULT_NEW)
    new_friends: int = field(default=DEFAULT_NEW)
    spider_id: int = field(default=DEFAULT_ICON_ID)
    x: Optional[str] = field(default=None)
    twitch: Optional[str] = field(default=None)
    diamonds: int = field(default=DEFAULT_DIAMONDS)
    explosion_id: int = field(default=DEFAULT_ICON_ID)
    role_id: int = field(default=DEFAULT_ID)
    comment_state: CommentState = field(default=CommentState.DEFAULT)
    color_3_id: int = field(default=DEFAULT_COLOR_3_ID)
    moons: int = field(default=DEFAULT_MOONS)
    swing_id: int = field(default=DEFAULT_ICON_ID)
    jetpack_id: int = field(default=DEFAULT_ICON_ID)
    demon_info: DemonInfo = field(factory=DemonInfo)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_profile(string)

        view = RobTopView(mapping)

        name = view.get_option(PROFILE_NAME).unwrap_or(EMPTY)

        id = view.get_option(PROFILE_ID).map(int).unwrap_or(DEFAULT_ID)

        stars = view.get_option(PROFILE_STARS).map(int).unwrap_or(DEFAULT_STARS)

        demons = view.get_option(PROFILE_DEMONS).map(int).unwrap_or(DEFAULT_DEMONS)

        creator_points = (
            view.get_option(PROFILE_CREATOR_POINTS).map(int).unwrap_or(DEFAULT_CREATOR_POINTS)
        )

        color_1_id = view.get_option(PROFILE_COLOR_1_ID).map(int).unwrap_or(DEFAULT_COLOR_1_ID)
        color_2_id = view.get_option(PROFILE_COLOR_2_ID).map(int).unwrap_or(DEFAULT_COLOR_2_ID)

        secret_coins = (
            view.get_option(PROFILE_SECRET_COINS).map(int).unwrap_or(DEFAULT_SECRET_COINS)
        )

        account_id = view.get_option(PROFILE_ACCOUNT_ID).map(int).unwrap_or(DEFAULT_ID)

        user_coins = view.get_option(PROFILE_USER_COINS).map(int).unwrap_or(DEFAULT_USER_COINS)

        message_state = (
            view.get_option(PROFILE_MESSAGE_STATE)
            .map(int)
            .map(MessageState)
            .unwrap_or(MessageState.DEFAULT)
        )

        friend_request_state = (
            view.get_option(PROFILE_FRIEND_REQUEST_STATE)
            .map(int)
            .map(FriendRequestState)
            .unwrap_or(FriendRequestState.DEFAULT)
        )

        youtube = view.get_option(PROFILE_YOUTUBE).filter(bool).extract()

        cube_id = view.get_option(PROFILE_CUBE_ID).map(int).unwrap_or(DEFAULT_ICON_ID)
        ship_id = view.get_option(PROFILE_SHIP_ID).map(int).unwrap_or(DEFAULT_ICON_ID)
        ball_id = view.get_option(PROFILE_BALL_ID).map(int).unwrap_or(DEFAULT_ICON_ID)
        ufo_id = view.get_option(PROFILE_UFO_ID).map(int).unwrap_or(DEFAULT_ICON_ID)
        wave_id = view.get_option(PROFILE_WAVE_ID).map(int).unwrap_or(DEFAULT_ICON_ID)
        robot_id = view.get_option(PROFILE_ROBOT_ID).map(int).unwrap_or(DEFAULT_ICON_ID)

        glow = view.get_option(PROFILE_GLOW).map(int_bool).unwrap_or(DEFAULT_GLOW)

        active = view.get_option(PROFILE_ACTIVE).map(int_bool).unwrap_or(DEFAULT_ACTIVE)

        rank = view.get_option(PROFILE_RANK).map(int).unwrap_or(DEFAULT_RANK)

        friend_state = (
            view.get_option(PROFILE_FRIEND_STATE)
            .map(int)
            .map(FriendState)
            .unwrap_or(FriendState.DEFAULT)
        )

        new_messages = view.get_option(PROFILE_NEW_MESSAGES).map(int).unwrap_or(DEFAULT_NEW)
        new_friend_requests = (
            view.get_option(PROFILE_NEW_FRIEND_REQUESTS).map(int).unwrap_or(DEFAULT_NEW)
        )
        new_friends = view.get_option(PROFILE_NEW_FRIENDS).map(int).unwrap_or(DEFAULT_NEW)

        spider_id = view.get_option(PROFILE_SPIDER_ID).map(int).unwrap_or(DEFAULT_ICON_ID)

        x = view.get_option(PROFILE_X).filter(bool).extract()

        twitch = view.get_option(PROFILE_TWITCH).filter(bool).extract()

        diamonds = view.get_option(PROFILE_DIAMONDS).map(int).unwrap_or(DEFAULT_DIAMONDS)

        explosion_id = view.get_option(PROFILE_EXPLOSION_ID).map(int).unwrap_or(DEFAULT_ICON_ID)

        role_id = view.get_option(PROFILE_ROLE_ID).map(int).unwrap_or(DEFAULT_ID)

        comment_state = (
            view.get_option(PROFILE_COMMENT_STATE)
            .map(int)
            .map(CommentState)
            .unwrap_or(CommentState.DEFAULT)
        )

        color_3_id = view.get_option(PROFILE_COLOR_3_ID).map(int).unwrap_or(color_2_id)

        moons = view.get_option(PROFILE_MOONS).map(int).unwrap_or(DEFAULT_MOONS)

        swing_id = view.get_option(PROFILE_SWING_ID).map(int).unwrap_or(DEFAULT_ICON_ID)

        jetpack_id = view.get_option(PROFILE_JETPACK_ID).map(int).unwrap_or(DEFAULT_ICON_ID)

        demon_info = (
            view.get_option(PROFILE_DEMON_INFO).map(DemonInfo.from_robtop).unwrap_or_else(DemonInfo)
        )

        return cls(
            name=name,
            id=id,
            stars=stars,
            demons=demons,
            creator_points=creator_points,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            secret_coins=secret_coins,
            account_id=account_id,
            user_coins=user_coins,
            message_state=message_state,
            friend_request_state=friend_request_state,
            youtube=youtube,
            cube_id=cube_id,
            ship_id=ship_id,
            ball_id=ball_id,
            ufo_id=ufo_id,
            wave_id=wave_id,
            robot_id=robot_id,
            glow=glow,
            active=active,
            rank=rank,
            friend_state=friend_state,
            new_messages=new_messages,
            new_friend_requests=new_friend_requests,
            new_friends=new_friends,
            spider_id=spider_id,
            x=x,
            twitch=twitch,
            diamonds=diamonds,
            explosion_id=explosion_id,
            role_id=role_id,
            comment_state=comment_state,
            color_3_id=color_3_id,
            moons=moons,
            swing_id=swing_id,
            jetpack_id=jetpack_id,
            demon_info=demon_info,
        )

    def to_robtop(self) -> str:
        mapping = {
            PROFILE_NAME: self.name,
            PROFILE_ID: str(self.id),
            PROFILE_STARS: str(self.stars),
            PROFILE_DEMONS: str(self.demons),
            PROFILE_CREATOR_POINTS: str(self.creator_points),
            PROFILE_COLOR_1_ID: str(self.color_1_id),
            PROFILE_COLOR_2_ID: str(self.color_2_id),
            PROFILE_SECRET_COINS: str(self.secret_coins),
            PROFILE_ACCOUNT_ID: str(self.account_id),
            PROFILE_USER_COINS: str(self.user_coins),
            PROFILE_MESSAGE_STATE: str(self.message_state.value),
            PROFILE_FRIEND_REQUEST_STATE: str(self.friend_request_state.value),
            PROFILE_YOUTUBE: self.youtube or EMPTY,
            PROFILE_CUBE_ID: str(self.cube_id),
            PROFILE_SHIP_ID: str(self.ship_id),
            PROFILE_BALL_ID: str(self.ball_id),
            PROFILE_UFO_ID: str(self.ufo_id),
            PROFILE_WAVE_ID: str(self.wave_id),
            PROFILE_ROBOT_ID: str(self.robot_id),
            PROFILE_GLOW: bool_str(self.has_glow()),
            PROFILE_ACTIVE: bool_str(self.is_active()),
            PROFILE_RANK: str(self.rank),
            PROFILE_FRIEND_STATE: str(self.friend_state.value),
            PROFILE_NEW_MESSAGES: str(self.new_messages),
            PROFILE_NEW_FRIEND_REQUESTS: str(self.new_friend_requests),
            PROFILE_NEW_FRIENDS: str(self.new_friends),
            PROFILE_SPIDER_ID: str(self.spider_id),
            PROFILE_X: self.x or EMPTY,
            PROFILE_TWITCH: self.twitch or EMPTY,
            PROFILE_DIAMONDS: str(self.diamonds),
            PROFILE_EXPLOSION_ID: str(self.explosion_id),
            PROFILE_ROLE_ID: str(self.role_id),
            PROFILE_COMMENT_STATE: str(self.comment_state.value),
            PROFILE_COLOR_3_ID: str(self.color_3_id),
            PROFILE_MOONS: str(self.moons),
            PROFILE_SWING_ID: str(self.swing_id),
            PROFILE_JETPACK_ID: str(self.jetpack_id),
            PROFILE_DEMON_INFO: self.demon_info.to_robtop(),
        }

        return concat_profile(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return PROFILE_SEPARATOR in string

    def has_glow(self) -> bool:
        return self.glow

    def is_active(self) -> bool:
        return self.active

    @property
    def banned(self) -> bool:
        return not self.active

    @banned.setter
    def banned(self, banned: bool) -> None:
        self.active = not self.banned

    def is_banned(self) -> bool:
        return self.banned


RELATIONSHIP_USER_NAME = 1
RELATIONSHIP_USER_ID = 2
RELATIONSHIP_USER_ICON_ID = 9
RELATIONSHIP_USER_COLOR_1_ID = 10
RELATIONSHIP_USER_COLOR_2_ID = 11
RELATIONSHIP_USER_ICON_TYPE = 14
RELATIONSHIP_USER_GLOW = 15
RELATIONSHIP_USER_ACCOUNT_ID = 16
RELATIONSHIP_USER_MESSAGE_STATE = 18


@define()
class RelationshipUserModel(Model):
    name: str = EMPTY
    id: int = DEFAULT_ID
    icon_id: int = DEFAULT_ICON_ID
    color_1_id: int = DEFAULT_COLOR_1_ID
    color_2_id: int = DEFAULT_COLOR_2_ID
    icon_type: IconType = IconType.DEFAULT
    glow: bool = DEFAULT_GLOW
    account_id: int = DEFAULT_ID
    message_state: MessageState = MessageState.DEFAULT

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_relationship_user(string)

        view = RobTopView(mapping)

        name = view.get_option(RELATIONSHIP_USER_NAME).unwrap_or(EMPTY)

        id = view.get_option(RELATIONSHIP_USER_ID).map(int).unwrap_or(DEFAULT_ID)

        icon_id = view.get_option(RELATIONSHIP_USER_ICON_ID).map(int).unwrap_or(DEFAULT_ICON_ID)

        color_1_id = (
            view.get_option(RELATIONSHIP_USER_COLOR_1_ID).map(int).unwrap_or(DEFAULT_COLOR_1_ID)
        )
        color_2_id = (
            view.get_option(RELATIONSHIP_USER_COLOR_2_ID).map(int).unwrap_or(DEFAULT_COLOR_2_ID)
        )

        icon_type = (
            view.get_option(RELATIONSHIP_USER_ICON_TYPE)
            .map(int)
            .map(IconType)
            .unwrap_or(IconType.DEFAULT)
        )

        glow = view.get_option(RELATIONSHIP_USER_GLOW).map(int_bool).unwrap_or(DEFAULT_GLOW)

        account_id = view.get_option(RELATIONSHIP_USER_ACCOUNT_ID).map(int).unwrap_or(DEFAULT_ID)

        message_state = (
            view.get_option(RELATIONSHIP_USER_MESSAGE_STATE)
            .map(int)
            .map(MessageState)
            .unwrap_or(MessageState.DEFAULT)
        )

        return cls(
            name=name,
            id=id,
            icon_id=icon_id,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            icon_type=icon_type,
            glow=glow,
            account_id=account_id,
            message_state=message_state,
        )

    def to_robtop(self) -> str:
        glow = self.has_glow()

        glow += glow  # type: ignore

        mapping = {
            RELATIONSHIP_USER_NAME: str(self.name),
            RELATIONSHIP_USER_ID: str(self.id),
            RELATIONSHIP_USER_ICON_ID: str(self.icon_id),
            RELATIONSHIP_USER_COLOR_1_ID: str(self.color_1_id),
            RELATIONSHIP_USER_COLOR_2_ID: str(self.color_2_id),
            RELATIONSHIP_USER_ICON_TYPE: str(self.icon_type.value),
            RELATIONSHIP_USER_GLOW: str(glow),
            RELATIONSHIP_USER_ACCOUNT_ID: str(self.account_id),
            RELATIONSHIP_USER_MESSAGE_STATE: str(self.message_state.value),
        }

        return concat_relationship_user(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return RELATIONSHIP_USER_SEPARATOR in string

    def has_glow(self) -> bool:
        return self.glow


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
LEADERBOARD_USER_MOONS = 52


@define()
class LeaderboardUserModel(Model):
    name: str = EMPTY
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
    moons: int = DEFAULT_MOONS

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_leaderboard_user(string)

        view = RobTopView(mapping)

        name = view.get_option(LEADERBOARD_USER_NAME).unwrap_or(EMPTY)

        id = view.get_option(LEADERBOARD_USER_ID).map(int).unwrap_or(DEFAULT_ID)

        stars = view.get_option(LEADERBOARD_USER_STARS).map(int).unwrap_or(DEFAULT_STARS)

        demons = view.get_option(LEADERBOARD_USER_DEMONS).map(int).unwrap_or(DEFAULT_DEMONS)

        place = view.get_option(LEADERBOARD_USER_PLACE).map(int).unwrap_or(DEFAULT_PLACE)

        creator_points = (
            view.get_option(LEADERBOARD_USER_CREATOR_POINTS)
            .map(int)
            .unwrap_or(DEFAULT_CREATOR_POINTS)
        )

        icon_id = view.get_option(LEADERBOARD_USER_ICON_ID).map(int).unwrap_or(DEFAULT_ICON_ID)

        color_1_id = (
            view.get_option(LEADERBOARD_USER_COLOR_1_ID).map(int).unwrap_or(DEFAULT_COLOR_1_ID)
        )
        color_2_id = (
            view.get_option(LEADERBOARD_USER_COLOR_2_ID).map(int).unwrap_or(DEFAULT_COLOR_2_ID)
        )

        secret_coins = (
            view.get_option(LEADERBOARD_USER_SECRET_COINS).map(int).unwrap_or(DEFAULT_SECRET_COINS)
        )

        icon_type = (
            view.get_option(LEADERBOARD_USER_ICON_TYPE)
            .map(int)
            .map(IconType)
            .unwrap_or(IconType.DEFAULT)
        )

        glow = view.get_option(LEADERBOARD_USER_GLOW).map(int_bool).unwrap_or(DEFAULT_GLOW)

        account_id = view.get_option(LEADERBOARD_USER_ACCOUNT_ID).map(int).unwrap_or(DEFAULT_ID)

        user_coins = (
            view.get_option(LEADERBOARD_USER_USER_COINS).map(int).unwrap_or(DEFAULT_USER_COINS)
        )

        diamonds = view.get_option(LEADERBOARD_USER_DIAMONDS).map(int).unwrap_or(DEFAULT_DIAMONDS)

        moons = view.get_option(LEADERBOARD_USER_MOONS).map(int).unwrap_or(DEFAULT_MOONS)

        return cls(
            name=name,
            id=id,
            stars=stars,
            demons=demons,
            place=place,
            creator_points=creator_points,
            icon_id=icon_id,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            secret_coins=secret_coins,
            icon_type=icon_type,
            glow=glow,
            account_id=account_id,
            user_coins=user_coins,
            diamonds=diamonds,
            moons=moons,
        )

    def to_robtop(self) -> str:
        glow = self.has_glow()

        glow += glow  # type: ignore

        mapping = {
            LEADERBOARD_USER_NAME: self.name,
            LEADERBOARD_USER_ID: str(self.id),
            LEADERBOARD_USER_STARS: str(self.stars),
            LEADERBOARD_USER_DEMONS: str(self.demons),
            LEADERBOARD_USER_PLACE: str(self.place),
            LEADERBOARD_USER_CREATOR_POINTS: str(self.creator_points),
            LEADERBOARD_USER_ICON_ID: str(self.icon_id),
            LEADERBOARD_USER_COLOR_1_ID: str(self.color_1_id),
            LEADERBOARD_USER_COLOR_2_ID: str(self.color_2_id),
            LEADERBOARD_USER_SECRET_COINS: str(self.secret_coins),
            LEADERBOARD_USER_ICON_TYPE: str(self.icon_type.value),
            LEADERBOARD_USER_GLOW: str(glow),
            LEADERBOARD_USER_ACCOUNT_ID: str(self.account_id),
            LEADERBOARD_USER_USER_COINS: str(self.user_coins),
            LEADERBOARD_USER_DIAMONDS: str(self.diamonds),
            LEADERBOARD_USER_MOONS: str(self.moons),
        }

        return concat_leaderboard_user(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEADERBOARD_USER_SEPARATOR in string

    def has_glow(self) -> bool:
        return self.glow


@define()
class TimelyInfoModel(Model):
    id: int = field(default=DEFAULT_ID)
    type: TimelyType = field(default=TimelyType.DEFAULT)
    cooldown: Duration = field(factory=duration)

    @classmethod
    def from_robtop(cls, string: str, type: TimelyType = TimelyType.DEFAULT) -> Self:
        id_string, cooldown_string = split_timely_info(string)

        id = int(id_string)
        cooldown = duration_from_seconds(float(cooldown_string))

        id %= WEEKLY_ID_ADD

        return cls(id=id, type=type, cooldown=cooldown)

    def to_robtop(self) -> str:
        id = self.id

        if self.type.is_weekly():
            id += WEEKLY_ID_ADD

        return iter.of(str(id), float_str(self.cooldown.total_seconds())).collect(
            concat_timely_info
        )

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

decode_message_content = decode_robtop_string_with(Key.MESSAGE)
encode_message_content = encode_robtop_string_with(Key.MESSAGE)


@define()
class MessageModel(Model):
    id: int = field(default=DEFAULT_ID)
    account_id: int = field(default=DEFAULT_ID)
    user_id: int = field(default=DEFAULT_ID)
    subject: str = field(default=EMPTY)
    content: str = field(default=EMPTY)
    name: str = field(default=EMPTY)
    created_at: DateTime = field(factory=utc_now)
    read: bool = field(default=DEFAULT_READ)
    sent: bool = field(default=DEFAULT_SENT)

    content_present: bool = field(default=DEFAULT_CONTENT_PRESENT)

    @classmethod
    def from_robtop(cls, string: str, content_present: bool = DEFAULT_CONTENT_PRESENT) -> Self:
        mapping = split_message(string)

        view = RobTopView(mapping)

        id = view.get_option(MESSAGE_ID).map(int).unwrap_or(DEFAULT_ID)

        account_id = view.get_option(MESSAGE_ACCOUNT_ID).map(int).unwrap_or(DEFAULT_ID)
        user_id = view.get_option(MESSAGE_USER_ID).map(int).unwrap_or(DEFAULT_ID)

        subject = (
            view.get_option(MESSAGE_SUBJECT).map(decode_base64_string_url_safe).unwrap_or(EMPTY)
        )

        content = view.get_option(MESSAGE_CONTENT).map(decode_message_content).unwrap_or(EMPTY)

        name = view.get_option(MESSAGE_NAME).unwrap_or(EMPTY)

        created_at = (
            view.get_option(MESSAGE_CREATED_AT)
            .map(option_date_time_from_human)
            .flatten()
            .unwrap_or_else(utc_now)
        )

        read = view.get_option(MESSAGE_READ).map(int_bool).unwrap_or(DEFAULT_READ)

        sent = view.get_option(MESSAGE_SENT).map(int_bool).unwrap_or(DEFAULT_SENT)

        return cls(
            id=id,
            account_id=account_id,
            user_id=user_id,
            subject=subject,
            content=content,
            name=name,
            created_at=created_at,
            read=read,
            sent=sent,
            content_present=content_present,
        )

    def to_robtop(self) -> str:
        mapping = {
            MESSAGE_ID: str(self.id),
            MESSAGE_ACCOUNT_ID: str(self.account_id),
            MESSAGE_USER_ID: str(self.user_id),
            MESSAGE_SUBJECT: encode_base64_string_url_safe(self.subject),
            MESSAGE_CONTENT: encode_message_content(self.content),
            MESSAGE_NAME: self.name,
            MESSAGE_CREATED_AT: date_time_to_human(self.created_at),
            MESSAGE_READ: bool_str(self.is_read()),
            MESSAGE_SENT: bool_str(self.is_sent()),
        }

        return concat_message(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return MESSAGE_SEPARATOR in string

    def is_read(self) -> bool:
        return self.read

    def is_sent(self) -> bool:
        return self.sent

    def has_content(self) -> bool:
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


@define()
class FriendRequestModel(Model):
    name: str = field(default=EMPTY)
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
    def from_robtop(cls, string: str) -> Self:
        mapping = split_friend_request(string)

        view = RobTopView(mapping)

        name = view.get_option(FRIEND_REQUEST_NAME).unwrap_or(EMPTY)

        user_id = view.get_option(FRIEND_REQUEST_USER_ID).map(int).unwrap_or(DEFAULT_ID)

        icon_id = view.get_option(FRIEND_REQUEST_ICON_ID).map(int).unwrap_or(DEFAULT_ICON_ID)

        color_1_id = (
            view.get_option(FRIEND_REQUEST_COLOR_1_ID).map(int).unwrap_or(DEFAULT_COLOR_1_ID)
        )
        color_2_id = (
            view.get_option(FRIEND_REQUEST_COLOR_2_ID).map(int).unwrap_or(DEFAULT_COLOR_2_ID)
        )

        icon_type = (
            view.get_option(FRIEND_REQUEST_ICON_TYPE)
            .map(int)
            .map(IconType)
            .unwrap_or(IconType.DEFAULT)
        )

        glow = view.get_option(FRIEND_REQUEST_GLOW).map(int_bool).unwrap_or(DEFAULT_GLOW)

        account_id = view.get_option(FRIEND_REQUEST_ACCOUNT_ID).map(int).unwrap_or(DEFAULT_ID)

        id = view.get_option(FRIEND_REQUEST_ID).map(int).unwrap_or(DEFAULT_ID)

        content = (
            view.get_option(FRIEND_REQUEST_CONTENT)
            .map(decode_base64_string_url_safe)
            .unwrap_or(EMPTY)
        )

        created_at = (
            view.get_option(FRIEND_REQUEST_CREATED_AT)
            .map(option_date_time_from_human)
            .flatten()
            .unwrap_or_else(utc_now)
        )

        unread = view.get_option(FRIEND_REQUEST_UNREAD).map(int_bool).unwrap_or(DEFAULT_UNREAD)

        return cls(
            name=name,
            user_id=user_id,
            icon_id=icon_id,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            icon_type=icon_type,
            glow=glow,
            account_id=account_id,
            id=id,
            content=content,
            created_at=created_at,
            unread=unread,
        )

    def to_robtop(self) -> str:
        glow = self.has_glow()

        glow += glow  # type: ignore

        unread = self.is_unread()

        unread_string = bool_str(unread) if unread else EMPTY

        mapping = {
            FRIEND_REQUEST_NAME: self.name,
            FRIEND_REQUEST_USER_ID: str(self.user_id),
            FRIEND_REQUEST_ICON_ID: str(self.icon_id),
            FRIEND_REQUEST_COLOR_1_ID: str(self.color_1_id),
            FRIEND_REQUEST_COLOR_2_ID: str(self.color_2_id),
            FRIEND_REQUEST_ICON_TYPE: str(self.icon_type.value),
            FRIEND_REQUEST_GLOW: str(glow),
            FRIEND_REQUEST_ACCOUNT_ID: str(self.account_id),
            FRIEND_REQUEST_ID: str(self.id),
            FRIEND_REQUEST_CONTENT: encode_base64_string_url_safe(self.content),
            FRIEND_REQUEST_CREATED_AT: date_time_to_human(self.created_at),
            FRIEND_REQUEST_UNREAD: unread_string,
        }

        return concat_friend_request(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return FRIEND_REQUEST_SEPARATOR in string

    def has_glow(self) -> bool:
        return self.glow

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
LEVEL_REWARD = 18
LEVEL_SCORE = 19
LEVEL_AUTO = 25
LEVEL_PASSWORD = 27
LEVEL_CREATED_AT = 28
LEVEL_UPDATED_AT = 29
LEVEL_ORIGINAL_ID = 30
LEVEL_TWO_PLAYER = 31
LEVEL_CUSTOM_SONG_ID = 35
LEVEL_CAPACITY = 36
LEVEL_COINS = 37
LEVEL_VERIFIED_COINS = 38
LEVEL_REQUESTED_REWARD = 39
LEVEL_LOW_DETAIL = 40
LEVEL_TIMELY_ID = 41
LEVEL_SPECIAL_RATE_TYPE = 42
LEVEL_DEMON_DIFFICULTY = 43
LEVEL_OBJECT_COUNT = 45
LEVEL_EDITOR_TIME = 46
LEVEL_COPIES_TIME = 47
LEVEL_TIME_STEPS = 57

UNPROCESSED_DATA = "unprocessed_data"


@define()
class LevelModel(Model):
    id: int = field(default=DEFAULT_ID)
    name: str = field(default=EMPTY)
    description: str = field(default=EMPTY)
    unprocessed_data: str = field(default=EMPTY)
    version: int = field(default=DEFAULT_VERSION)
    creator_id: int = field(default=DEFAULT_ID)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT)
    downloads: int = field(default=DEFAULT_DOWNLOADS)
    official_song_id: int = field(default=DEFAULT_ID)
    game_version: GameVersion = field(default=CURRENT_GAME_VERSION)
    rating: int = field(default=DEFAULT_RATING)
    length: LevelLength = field(default=LevelLength.DEFAULT)
    reward: EitherReward = field(factory=EitherReward)
    score: int = field(default=DEFAULT_SCORE)
    password: Password = field(factory=Password)
    created_at: DateTime = field(factory=utc_now)
    updated_at: DateTime = field(factory=utc_now)
    original_id: int = field(default=DEFAULT_ID)
    two_player: bool = field(default=DEFAULT_TWO_PLAYER)
    custom_song_id: int = field(default=DEFAULT_ID)
    capacity: Capacity = field(factory=Capacity)
    coins: int = field(default=DEFAULT_COINS)
    verified_coins: bool = field(default=DEFAULT_VERIFIED_COINS)
    requested_reward: EitherReward = field(factory=EitherReward)
    low_detail: bool = field(default=DEFAULT_LOW_DETAIL)
    timely_id: int = field(default=DEFAULT_ID)
    timely_type: TimelyType = field(default=TimelyType.DEFAULT)
    special_rate_type: SpecialRateType = field(default=SpecialRateType.DEFAULT)
    object_count: int = field(default=DEFAULT_OBJECT_COUNT)
    editor_time: Duration = field(factory=duration)
    copies_time: Duration = field(factory=duration)
    time_steps: int = field(default=DEFAULT_TIME_STEPS)
    platformer: bool = field(default=DEFAULT_PLATFORMER)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_level(string)

        view = RobTopView(mapping)

        id = view.get_option(LEVEL_ID).map(int).unwrap_or(DEFAULT_ID)

        name = view.get_option(LEVEL_NAME).unwrap_or(EMPTY)

        description = (
            view.get_option(LEVEL_DESCRIPTION).map(decode_base64_string_url_safe).unwrap_or(EMPTY)
        )

        unprocessed_data = mapping.get(LEVEL_UNPROCESSED_DATA, EMPTY)

        unprocessed_data = mapping.get(LEVEL_UNPROCESSED_DATA, EMPTY)

        if Editor.can_be_in(unprocessed_data):
            unprocessed_data = zip_level_string(unprocessed_data)

        version = view.get_option(LEVEL_VERSION).map(int).unwrap_or(DEFAULT_VERSION)

        creator_id = view.get_option(LEVEL_CREATOR_ID).map(int).unwrap_or(DEFAULT_ID)

        difficulty_numerator = (
            view.get_option(LEVEL_DIFFICULTY_NUMERATOR).map(int).unwrap_or(DEFAULT_NUMERATOR)
        )
        difficulty_denominator = (
            view.get_option(LEVEL_DIFFICULTY_DENOMINATOR).map(int).unwrap_or(DEFAULT_DENOMINATOR)
        )

        demon_difficulty_value = (
            view.get_option(LEVEL_DEMON_DIFFICULTY)
            .map(int)
            .unwrap_or(DemonDifficulty.DEFAULT.value)
        )

        auto = view.get_option(LEVEL_AUTO).map(int_bool).unwrap_or(DEFAULT_AUTO)
        demon = view.get_option(LEVEL_DEMON).map(int_bool).unwrap_or(DEFAULT_DEMON)

        difficulty = DifficultyParameters(
            difficulty_numerator=difficulty_numerator,
            difficulty_denominator=difficulty_denominator,
            demon_difficulty_value=demon_difficulty_value,
            auto=auto,
            demon=demon,
        ).into_difficulty()

        downloads = view.get_option(LEVEL_DOWNLOADS).map(int).unwrap_or(DEFAULT_DOWNLOADS)

        official_song_id = view.get_option(LEVEL_OFFICIAL_SONG_ID).map(int).unwrap_or(DEFAULT_ID)

        game_version = (
            view.get_option(LEVEL_GAME_VERSION)
            .map(GameVersion.from_robtop)
            .unwrap_or(CURRENT_GAME_VERSION)
        )

        rating = view.get_option(LEVEL_RATING).map(int).unwrap_or(DEFAULT_RATING)

        length = (
            view.get_option(LEVEL_LENGTH).map(int).map(LevelLength).unwrap_or(LevelLength.DEFAULT)
        )

        platformer = length.is_platformer()

        reward_count = view.get_option(LEVEL_REWARD).map(int).unwrap_or(DEFAULT_COUNT)

        reward = EitherReward(reward_count, platformer)

        score = max(0, view.get_option(LEVEL_SCORE).map(int).unwrap_or(DEFAULT_SCORE))

        password = (
            view.get_option(LEVEL_PASSWORD).map(Password.from_robtop).unwrap_or_else(Password)
        )

        created_at = (
            view.get_option(LEVEL_CREATED_AT)
            .map(option_date_time_from_human)
            .flatten()
            .unwrap_or_else(utc_now)
        )

        updated_at = (
            view.get_option(LEVEL_UPDATED_AT)
            .map(option_date_time_from_human)
            .flatten()
            .unwrap_or_else(utc_now)
        )

        original_id = view.get_option(LEVEL_ORIGINAL_ID).map(int).unwrap_or(DEFAULT_ID)

        two_player = view.get_option(LEVEL_TWO_PLAYER).map(int_bool).unwrap_or(DEFAULT_TWO_PLAYER)

        custom_song_id = view.get_option(LEVEL_CUSTOM_SONG_ID).map(int).unwrap_or(DEFAULT_ID)

        capacity = (
            view.get_option(LEVEL_CAPACITY).map(Capacity.from_robtop).unwrap_or_else(Capacity)
        )

        coins = view.get_option(LEVEL_COINS).map(int).unwrap_or(DEFAULT_COINS)

        verified_coins = (
            view.get_option(LEVEL_VERIFIED_COINS).map(int_bool).unwrap_or(DEFAULT_VERIFIED_COINS)
        )

        requested_reward_count = (
            view.get_option(LEVEL_REQUESTED_REWARD).map(int).unwrap_or(DEFAULT_COUNT)
        )

        requested_reward = EitherReward(requested_reward_count, platformer)

        low_detail = view.get_option(LEVEL_LOW_DETAIL).map(int_bool).unwrap_or(DEFAULT_LOW_DETAIL)

        timely_id = view.get_option(LEVEL_TIMELY_ID).map(int).unwrap_or(DEFAULT_ID)

        if timely_id:
            result, timely_id = divmod(timely_id, WEEKLY_ID_ADD)

            if result:
                timely_type = TimelyType.WEEKLY

            else:
                timely_type = TimelyType.DAILY

        else:
            timely_type = TimelyType.NOT_TIMELY

        special_rate_type = (
            view.get_option(LEVEL_SPECIAL_RATE_TYPE)
            .map(int)
            .map(SpecialRateType)
            .unwrap_or(SpecialRateType.DEFAULT)
        )

        object_count = view.get_option(LEVEL_OBJECT_COUNT).map(int).unwrap_or(DEFAULT_OBJECT_COUNT)

        editor_time = (
            view.get_option(LEVEL_EDITOR_TIME)
            .filter(bool)
            .map(float)
            .map(duration_from_seconds)
            .unwrap_or_else(duration)
        )

        copies_time = (
            view.get_option(LEVEL_COPIES_TIME)
            .filter(bool)
            .map(float)
            .map(duration_from_seconds)
            .unwrap_or_else(duration)
        )

        time_steps = (
            view.get_option(LEVEL_TIME_STEPS)
            .map(option_int)
            .flatten()
            .unwrap_or(DEFAULT_TIME_STEPS)
        )

        return cls(
            id=id,
            name=name,
            description=description,
            unprocessed_data=unprocessed_data,
            version=version,
            creator_id=creator_id,
            difficulty=difficulty,
            downloads=downloads,
            official_song_id=official_song_id,
            game_version=game_version,
            rating=rating,
            length=length,
            reward=reward,
            score=score,
            password=password,
            created_at=created_at,
            updated_at=updated_at,
            original_id=original_id,
            two_player=two_player,
            custom_song_id=custom_song_id,
            capacity=capacity,
            coins=coins,
            verified_coins=verified_coins,
            requested_reward=requested_reward,
            low_detail=low_detail,
            timely_id=timely_id,
            timely_type=timely_type,
            special_rate_type=special_rate_type,
            object_count=object_count,
            editor_time=editor_time,
            copies_time=copies_time,
            time_steps=time_steps,
            platformer=platformer,
        )

    def to_robtop(self) -> str:
        timely_id = self.timely_id

        if self.timely_type.is_weekly():
            timely_id += WEEKLY_ID_ADD

        difficulty_parameters = DifficultyParameters.from_difficulty(self.difficulty)

        demon = difficulty_parameters.is_demon()

        demon_string = bool_str(demon) if demon else EMPTY

        auto = difficulty_parameters.is_auto()

        auto_string = bool_str(auto) if auto else EMPTY

        two_player = self.is_two_player()

        two_player_string = bool_str(two_player) if two_player else EMPTY

        mapping = {
            LEVEL_ID: str(self.id),
            LEVEL_NAME: self.name,
            LEVEL_DESCRIPTION: encode_base64_string_url_safe(self.description),
            LEVEL_UNPROCESSED_DATA: self.unprocessed_data,
            LEVEL_VERSION: str(self.version),
            LEVEL_CREATOR_ID: str(self.creator_id),
            LEVEL_DIFFICULTY_DENOMINATOR: str(difficulty_parameters.difficulty_denominator),
            LEVEL_DIFFICULTY_NUMERATOR: str(difficulty_parameters.difficulty_numerator),
            LEVEL_DOWNLOADS: str(self.downloads),
            LEVEL_OFFICIAL_SONG_ID: str(self.official_song_id),
            LEVEL_GAME_VERSION: self.game_version.to_robtop(),
            LEVEL_RATING: str(self.rating),
            LEVEL_LENGTH: str(self.length.value),
            LEVEL_DEMON: demon_string,
            LEVEL_REWARD: str(self.reward.count),
            LEVEL_SCORE: str(self.score),
            LEVEL_AUTO: auto_string,
            LEVEL_PASSWORD: self.password.to_robtop(),
            LEVEL_CREATED_AT: date_time_to_human(self.created_at),
            LEVEL_UPDATED_AT: date_time_to_human(self.updated_at),
            LEVEL_ORIGINAL_ID: str(self.original_id),
            LEVEL_TWO_PLAYER: two_player_string,
            LEVEL_CUSTOM_SONG_ID: str(self.custom_song_id),
            LEVEL_CAPACITY: self.capacity.to_robtop(),
            LEVEL_COINS: str(self.coins),
            LEVEL_VERIFIED_COINS: bool_str(self.has_verified_coins()),
            LEVEL_REQUESTED_REWARD: str(self.requested_reward.count),
            LEVEL_LOW_DETAIL: bool_str(self.has_low_detail()),
            LEVEL_TIMELY_ID: str(timely_id),
            LEVEL_SPECIAL_RATE_TYPE: str(self.special_rate_type.value),
            LEVEL_DEMON_DIFFICULTY: str(difficulty_parameters.demon_difficulty_value),
            LEVEL_OBJECT_COUNT: str(self.object_count),
            LEVEL_EDITOR_TIME: float_str(self.editor_time.total_seconds()),
            LEVEL_COPIES_TIME: float_str(self.copies_time.total_seconds()),
            LEVEL_TIME_STEPS: str(self.time_steps),
        }

        return concat_level(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_SEPARATOR in string

    def is_two_player(self) -> bool:
        return self.two_player

    def has_low_detail(self) -> bool:
        return self.low_detail

    def is_epic(self) -> bool:
        return self.special_rate_type.is_epic()

    def is_legendary(self) -> bool:
        return self.special_rate_type.is_legendary()

    def is_mythic(self) -> bool:
        return self.special_rate_type.is_mythic()

    def is_platformer(self) -> bool:
        return self.platformer

    def has_verified_coins(self) -> bool:
        return self.verified_coins

    @property
    @cache_by(UNPROCESSED_DATA)
    def processed_data(self) -> str:
        return unzip_level_string(self.unprocessed_data)

    @processed_data.setter
    def processed_data(self, data: str) -> None:
        self.unprocessed_data = zip_level_string(data)

    @property
    @cache_by(UNPROCESSED_DATA)
    def data(self) -> bytes:
        return Editor.from_robtop(self.processed_data).to_bytes()

    @data.setter
    def data(self, data: bytes) -> None:
        self.processed_data = Editor.from_bytes(data).to_robtop()


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
    def from_robtop(cls, string: str) -> Self:
        mapping = split_level_comment_inner(string)

        view = RobTopView(mapping)

        level_id = view.get_option(LEVEL_COMMENT_INNER_LEVEL_ID).map(int).unwrap_or(DEFAULT_ID)

        content = (
            view.get_option(LEVEL_COMMENT_INNER_CONTENT)
            .map(decode_base64_string_url_safe)
            .unwrap_or(EMPTY)
        )

        user_id = view.get_option(LEVEL_COMMENT_INNER_USER_ID).map(int).unwrap_or(DEFAULT_ID)

        rating = view.get_option(LEVEL_COMMENT_INNER_RATING).map(int).unwrap_or(DEFAULT_RATING)

        id = view.get_option(LEVEL_COMMENT_INNER_ID).map(int).unwrap_or(DEFAULT_ID)

        spam = view.get_option(LEVEL_COMMENT_INNER_SPAM).map(int_bool).unwrap_or(DEFAULT_SPAM)

        created_at = (
            view.get_option(LEVEL_COMMENT_INNER_CREATED_AT)
            .map(option_date_time_from_human)
            .flatten()
            .unwrap_or_else(utc_now)
        )

        record = view.get_option(LEVEL_COMMENT_INNER_RECORD).map(int).unwrap_or(DEFAULT_RECORD)

        role_id = view.get_option(LEVEL_COMMENT_INNER_ROLE_ID).map(int).unwrap_or(DEFAULT_ID)

        color = (
            view.get_option(LEVEL_COMMENT_INNER_COLOR)
            .map(Color.from_robtop)
            .unwrap_or_else(Color.default)
        )

        return cls(
            level_id=level_id,
            content=content,
            user_id=user_id,
            rating=rating,
            id=id,
            spam=spam,
            created_at=created_at,
            record=record,
            role_id=role_id,
            color=color,
        )

    def to_robtop(self) -> str:
        mapping = {
            LEVEL_COMMENT_INNER_LEVEL_ID: str(self.level_id),
            LEVEL_COMMENT_INNER_CONTENT: encode_base64_string_url_safe(self.content),
            LEVEL_COMMENT_INNER_USER_ID: str(self.user_id),
            LEVEL_COMMENT_INNER_RATING: str(self.rating),
            LEVEL_COMMENT_INNER_ID: str(self.id),
            LEVEL_COMMENT_INNER_SPAM: bool_str(self.spam),
            LEVEL_COMMENT_INNER_CREATED_AT: date_time_to_human(self.created_at),
            LEVEL_COMMENT_INNER_RECORD: str(self.record),
            LEVEL_COMMENT_INNER_ROLE_ID: str(self.role_id),
            LEVEL_COMMENT_INNER_COLOR: self.color.to_robtop(),
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


@define()
class LevelCommentUserModel(Model):
    name: str = EMPTY
    icon_id: int = DEFAULT_ICON_ID
    color_1_id: int = DEFAULT_COLOR_1_ID
    color_2_id: int = DEFAULT_COLOR_2_ID
    icon_type: IconType = IconType.DEFAULT
    glow: bool = DEFAULT_GLOW
    account_id: int = DEFAULT_ID

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_level_comment_user(string)

        view = RobTopView(mapping)

        name = view.get_option(LEVEL_COMMENT_USER_NAME).unwrap_or(EMPTY)

        icon_id = view.get_option(LEVEL_COMMENT_USER_ICON_ID).map(int).unwrap_or(DEFAULT_ICON_ID)

        color_1_id = (
            view.get_option(LEVEL_COMMENT_USER_COLOR_1_ID).map(int).unwrap_or(DEFAULT_COLOR_1_ID)
        )
        color_2_id = (
            view.get_option(LEVEL_COMMENT_USER_COLOR_2_ID).map(int).unwrap_or(DEFAULT_COLOR_2_ID)
        )

        icon_type = (
            view.get_option(LEVEL_COMMENT_USER_ICON_TYPE)
            .map(int)
            .map(IconType)
            .unwrap_or(IconType.DEFAULT)
        )

        glow = view.get_option(LEVEL_COMMENT_USER_GLOW).map(int_bool).unwrap_or(DEFAULT_GLOW)

        account_id = view.get_option(LEVEL_COMMENT_USER_ACCOUNT_ID).map(int).unwrap_or(DEFAULT_ID)

        return cls(
            name=name,
            icon_id=icon_id,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            icon_type=icon_type,
            glow=glow,
            account_id=account_id,
        )

    def to_robtop(self) -> str:
        glow = self.has_glow()

        glow += glow  # type: ignore

        mapping = {
            LEVEL_COMMENT_USER_NAME: self.name,
            LEVEL_COMMENT_USER_ICON_ID: str(self.icon_id),
            LEVEL_COMMENT_USER_COLOR_1_ID: str(self.color_1_id),
            LEVEL_COMMENT_USER_COLOR_2_ID: str(self.color_2_id),
            LEVEL_COMMENT_USER_ICON_TYPE: str(self.icon_type.value),
            LEVEL_COMMENT_USER_GLOW: str(glow),
            LEVEL_COMMENT_USER_ACCOUNT_ID: str(self.account_id),
        }

        return concat_level_comment_user(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_COMMENT_USER_SEPARATOR in string

    def has_glow(self) -> bool:
        return self.glow


@define()
class LevelCommentModel(Model):
    inner: LevelCommentInnerModel = field(factory=LevelCommentInnerModel)
    user: LevelCommentUserModel = field(factory=LevelCommentUserModel)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        inner_string, user_string = split_level_comment(string)

        inner = LevelCommentInnerModel.from_robtop(inner_string)
        user = LevelCommentUserModel.from_robtop(user_string)

        return cls(inner=inner, user=user)

    def to_robtop(self) -> str:
        return iter.of(self.inner.to_robtop(), self.user.to_robtop()).collect(concat_level_comment)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_COMMENT_SEPARATOR in string


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
    def from_robtop(cls, string: str) -> Self:
        mapping = split_user_comment(string)

        view = RobTopView(mapping)

        content = (
            view.get_option(USER_COMMENT_CONTENT)
            .map(decode_base64_string_url_safe)
            .unwrap_or(EMPTY)
        )

        rating = view.get_option(USER_COMMENT_RATING).map(int).unwrap_or(DEFAULT_RATING)

        id = view.get_option(USER_COMMENT_ID).map(int).unwrap_or(DEFAULT_ID)

        created_at = (
            view.get_option(USER_COMMENT_CREATED_AT)
            .map(option_date_time_from_human)
            .flatten()
            .unwrap_or_else(utc_now)
        )

        return cls(content=content, rating=rating, id=id, created_at=created_at)

    def to_robtop(self) -> str:
        mapping = {
            USER_COMMENT_CONTENT: decode_base64_string_url_safe(self.content),
            USER_COMMENT_RATING: str(self.rating),
            USER_COMMENT_ID: str(self.id),
            USER_COMMENT_CREATED_AT: date_time_to_human(self.created_at),
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


@define()
class LevelLeaderboardUserModel(Model):
    name: str = field(default=EMPTY)
    id: int = field(default=DEFAULT_ID)
    either_record: EitherRecord = field(factory=EitherRecord)
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
    def from_robtop(cls, string: str, platformer: bool = DEFAULT_PLATFORMER) -> Self:
        mapping = split_level_leaderboard_user(string)

        view = RobTopView(mapping)

        name = view.get_option(LEVEL_LEADERBOARD_USER_NAME).unwrap_or(EMPTY)

        id = view.get_option(LEVEL_LEADERBOARD_USER_ID).map(int).unwrap_or(DEFAULT_ID)

        record = view.get_option(LEVEL_LEADERBOARD_USER_RECORD).map(int).unwrap_or(DEFAULT_RECORD)

        either_record = EitherRecord(record, platformer)

        place = view.get_option(LEVEL_LEADERBOARD_USER_PLACE).map(int).unwrap_or(DEFAULT_PLACE)

        icon_id = (
            view.get_option(LEVEL_LEADERBOARD_USER_ICON_ID).map(int).unwrap_or(DEFAULT_ICON_ID)
        )

        color_1_id = (
            view.get_option(LEVEL_LEADERBOARD_USER_COLOR_1_ID)
            .map(int)
            .unwrap_or(DEFAULT_COLOR_1_ID)
        )
        color_2_id = (
            view.get_option(LEVEL_LEADERBOARD_USER_COLOR_2_ID)
            .map(int)
            .unwrap_or(DEFAULT_COLOR_2_ID)
        )

        coins = view.get_option(LEVEL_LEADERBOARD_USER_COINS).map(int).unwrap_or(DEFAULT_COINS)

        icon_type = (
            view.get_option(LEVEL_LEADERBOARD_USER_ICON_TYPE)
            .map(int)
            .map(IconType)
            .unwrap_or(IconType.DEFAULT)
        )

        glow = view.get_option(LEVEL_LEADERBOARD_USER_GLOW).map(int_bool).unwrap_or(DEFAULT_GLOW)

        recorded_at = (
            view.get_option(LEVEL_LEADERBOARD_USER_RECORDED_AT)
            .map(option_date_time_from_human)
            .flatten()
            .unwrap_or_else(utc_now)
        )

        return cls(
            name=name,
            id=id,
            either_record=either_record,
            place=place,
            icon_id=icon_id,
            color_1_id=color_1_id,
            color_2_id=color_2_id,
            coins=coins,
            icon_type=icon_type,
            glow=glow,
            recorded_at=recorded_at,
        )

    def to_robtop(self) -> str:
        glow = self.has_glow()

        glow += glow  # type: ignore

        mapping = {
            LEVEL_LEADERBOARD_USER_NAME: self.name,
            LEVEL_LEADERBOARD_USER_ID: str(self.id),
            LEVEL_LEADERBOARD_USER_RECORD: str(self.either_record.record),
            LEVEL_LEADERBOARD_USER_PLACE: str(self.place),
            LEVEL_LEADERBOARD_USER_ICON_ID: str(self.icon_id),
            LEVEL_LEADERBOARD_USER_COLOR_1_ID: str(self.color_1_id),
            LEVEL_LEADERBOARD_USER_COLOR_2_ID: str(self.color_2_id),
            LEVEL_LEADERBOARD_USER_COINS: str(self.coins),
            LEVEL_LEADERBOARD_USER_ICON_TYPE: str(self.icon_type.value),
            LEVEL_LEADERBOARD_USER_GLOW: str(glow),
            LEVEL_LEADERBOARD_USER_ACCOUNT_ID: str(self.account_id),
            LEVEL_LEADERBOARD_USER_RECORDED_AT: date_time_to_human(self.recorded_at),
        }

        return concat_level_leaderboard_user(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_LEADERBOARD_USER_SEPARATOR in string

    def has_glow(self) -> bool:
        return self.glow


ARTIST_NAME = 4


@define()
class ArtistModel(Model):
    name: str = EMPTY

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_artist(string)

        view = RobTopView(mapping)

        name = view.get_option(ARTIST_NAME).unwrap_or(EMPTY)

        return cls(name=name)

    def to_robtop(self) -> str:
        mapping = {ARTIST_NAME: self.name}

        return concat_artist(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return ARTIST_SEPARATOR in string


@define()
class ChestModel(Model):
    orbs: int = DEFAULT_ORBS
    diamonds: int = DEFAULT_DIAMONDS
    shard_type: ShardType = ShardType.DEFAULT
    keys: int = DEFAULT_KEYS

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        orbs, diamonds, shard_type_value, keys = iter(split_chest(string)).map(int).tuple()

        shard_type = ShardType(shard_type_value)

        return cls(orbs=orbs, diamonds=diamonds, shard_type=shard_type, keys=keys)

    def to_robtop(self) -> str:
        return iter.of(
            str(self.orbs),
            str(self.diamonds),
            str(self.shard_type.value),
            str(self.keys),
        ).collect(concat_chest)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return CHEST_SEPARATOR in string


@define()
class QuestModel(Model):
    id: int = DEFAULT_ID
    type: QuestType = QuestType.DEFAULT
    amount: int = DEFAULT_AMOUNT
    reward: int = DEFAULT_REWARD
    name: str = EMPTY

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        id_string, type_string, amount_string, reward_string, name = split_quest(string)

        id = int(id_string)

        type_value = int(type_string)

        type = QuestType(type_value)

        amount = int(amount_string)

        reward = int(reward_string)

        return cls(id=id, type=type, amount=amount, reward=reward, name=name)

    def to_robtop(self) -> str:
        return iter.of(
            str(self.id),
            str(self.type.value),
            str(self.amount),
            str(self.reward),
            self.name,
        ).collect(concat_quest)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return QUEST_SEPARATOR in string


GAUNTLET_ID = 1
GAUNTLET_LEVEL_IDS = 3


@define()
class GauntletModel(Model):
    id: int = DEFAULT_ID
    level_ids: DynamicTuple[int] = ()

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_gauntlet(string)

        view = RobTopView(mapping)

        id = view.get_option(GAUNTLET_ID).map(int).unwrap_or(DEFAULT_ID)

        level_ids = (
            view.get_option(GAUNTLET_LEVEL_IDS)
            .map(split_level_ids)
            .map(iter)
            .unwrap_or_else(iter.empty)
            .map(int)
            .tuple()
        )

        return cls(id=id, level_ids=level_ids)

    def to_robtop(self) -> str:
        mapping = {
            GAUNTLET_ID: str(self.id),
            GAUNTLET_LEVEL_IDS: iter(self.level_ids).map(str).collect(concat_level_ids),
        }

        return concat_gauntlet(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return GAUNTLET_SEPARATOR in string


MAP_PACK_ID = 1
MAP_PACK_NAME = 2
MAP_PACK_LEVEL_IDS = 3
MAP_PACK_STARS = 4
MAP_PACK_COINS = 5
MAP_PACK_DIFFICULTY = 6
MAP_PACK_COLOR = 7
MAP_PACK_OTHER_COLOR = 8


@define()
class MapPackModel(Model):
    id: int = field(default=DEFAULT_ID)
    name: str = field(default=EMPTY)
    level_ids: DynamicTuple[int] = field(default=())
    stars: int = field(default=DEFAULT_STARS)
    coins: int = field(default=DEFAULT_COINS)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT)
    color: Color = field(factory=Color.default)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        mapping = split_map_pack(string)

        view = RobTopView(mapping)

        id = view.get_option(MAP_PACK_ID).map(int).unwrap_or(DEFAULT_ID)

        name = view.get_option(MAP_PACK_NAME).unwrap_or(EMPTY)

        level_ids = (
            view.get_option(MAP_PACK_LEVEL_IDS)
            .map(split_level_ids)
            .map(iter)
            .unwrap_or_else(iter.empty)
            .map(int)
            .tuple()
        )

        stars = view.get_option(MAP_PACK_STARS).map(int).unwrap_or(DEFAULT_STARS)

        coins = view.get_option(MAP_PACK_COINS).map(int).unwrap_or(DEFAULT_COINS)

        difficulty = (
            view.get_option(MAP_PACK_DIFFICULTY)
            .map(int)
            .map(increment)  # slightly hacky way of conversion
            .map(Difficulty)
            .unwrap_or(Difficulty.DEFAULT)
        )

        color = view.get_option(MAP_PACK_COLOR).map(Color.from_robtop).unwrap_or_else(Color.default)

        return cls(
            id=id,
            name=name,
            level_ids=level_ids,
            stars=stars,
            coins=coins,
            difficulty=difficulty,
            color=color,
        )

    def to_robtop(self) -> str:
        mapping = {
            MAP_PACK_ID: str(self.id),
            MAP_PACK_NAME: self.name,
            MAP_PACK_LEVEL_IDS: iter(self.level_ids).map(str).collect(concat_level_ids),
            MAP_PACK_STARS: str(self.stars),
            MAP_PACK_COINS: str(self.coins),
            MAP_PACK_DIFFICULTY: str(decrement(self.difficulty.value)),
            MAP_PACK_COLOR: self.color.to_robtop(),
            MAP_PACK_OTHER_COLOR: self.color.to_robtop(),
        }

        return concat_map_pack(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return MAP_PACK_SEPARATOR in string


@define()
class ChestsInnerModel(Model):
    random_string: str = field(default=EMPTY)
    user_id: int = field(default=DEFAULT_ID)
    check: str = field(default=EMPTY)
    udid: str = field(default=EMPTY)
    account_id: int = field(default=DEFAULT_ID)
    chest_1_duration: Duration = field(factory=duration)
    chest_1: ChestModel = field(factory=ChestModel)
    chest_1_count: int = field(default=DEFAULT_CHEST_COUNT)
    chest_2_duration: Duration = field(factory=duration)
    chest_2: ChestModel = field(factory=ChestModel)
    chest_2_count: int = field(default=DEFAULT_CHEST_COUNT)
    reward_type: RewardType = field(default=RewardType.DEFAULT)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        (
            random_string,
            user_id_string,
            check,
            udid,
            account_id_string,
            chest_1_duration_string,
            chest_1_string,
            chest_1_count_string,
            chest_2_duration_string,
            chest_2_string,
            chest_2_count_string,
            reward_type_string,
        ) = split_chests_inner(string)

        user_id = int(user_id_string)

        account_id = int(account_id_string)

        chest_1_duration = duration_from_seconds(float(chest_1_duration_string))

        chest_1 = ChestModel.from_robtop(chest_1_string)

        chest_1_count = int(chest_1_count_string)

        chest_2_duration = duration_from_seconds(float(chest_2_duration_string))

        chest_2 = ChestModel.from_robtop(chest_2_string)

        chest_2_count = int(chest_2_count_string)

        reward_type_value = int(reward_type_string)

        reward_type = RewardType(reward_type_value)

        return cls(
            random_string=random_string,
            user_id=user_id,
            check=check,
            udid=udid,
            account_id=account_id,
            chest_1_duration=chest_1_duration,
            chest_1=chest_1,
            chest_1_count=chest_1_count,
            chest_2_duration=chest_2_duration,
            chest_2=chest_2,
            chest_2_count=chest_2_count,
            reward_type=reward_type,
        )

    def to_robtop(self) -> str:
        return iter.of(
            self.random_string,
            str(self.user_id),
            self.check,
            self.udid,
            str(self.account_id),
            float_str(self.chest_1_duration.total_seconds()),
            self.chest_1.to_robtop(),
            str(self.chest_1_count),
            float_str(self.chest_2_duration.total_seconds()),
            self.chest_2.to_robtop(),
            str(self.chest_2_count),
            str(self.reward_type.value),
        ).collect(concat_chests_inner)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return CHESTS_INNER_SEPARATOR in string


@define()
class QuestsInnerModel(Model):
    random_string: str = field(default=EMPTY)
    user_id: int = field(default=DEFAULT_ID)
    check: str = field(default=EMPTY)
    udid: str = field(default=EMPTY)
    account_id: int = field(default=DEFAULT_ID)
    quest_duration: Duration = field(factory=duration)
    quest_1: QuestModel = field(factory=QuestModel)
    quest_2: QuestModel = field(factory=QuestModel)
    quest_3: QuestModel = field(factory=QuestModel)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        (
            random_string,
            user_id_string,
            check,
            udid,
            account_id_string,
            duration_string,
            quest_1_string,
            quest_2_string,
            quest_3_string,
        ) = split_quests_inner(string)

        user_id = int(user_id_string)

        account_id = int(account_id_string)

        quest_duration = duration_from_seconds(float(duration_string))

        quest_1 = QuestModel.from_robtop(quest_1_string)
        quest_2 = QuestModel.from_robtop(quest_2_string)
        quest_3 = QuestModel.from_robtop(quest_3_string)

        return cls(
            random_string=random_string,
            user_id=user_id,
            check=check,
            udid=udid,
            account_id=account_id,
            quest_duration=quest_duration,
            quest_1=quest_1,
            quest_2=quest_2,
            quest_3=quest_3,
        )

    def to_robtop(self) -> str:
        return iter.of(
            self.random_string,
            str(self.user_id),
            self.check,
            self.udid,
            str(self.account_id),
            float_str(self.quest_duration.total_seconds()),
            self.quest_1.to_robtop(),
            self.quest_2.to_robtop(),
            self.quest_3.to_robtop(),
        ).collect(concat_quests_inner)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return QUESTS_INNER_SEPARATOR in string


decode_chests_inner = decode_robtop_string_with(Key.CHESTS)
encode_chests_inner = encode_robtop_string_with(Key.CHESTS)


@define()
class ChestsResponseModel(Model):
    inner: ChestsInnerModel = field(factory=ChestsInnerModel)
    hash: str = field()

    @hash.default
    def default_hash(self) -> str:
        return self.compute_hash()

    def compute_hash(self) -> str:
        return sha1_string_with_salt(self.encode_inner(), Salt.CHESTS)

    def encode_inner(self) -> str:
        return generate_random_string(CHESTS_SLICE) + encode_chests_inner(self.inner.to_robtop())

    @classmethod
    def decode_inner(cls, string: str) -> str:
        return decode_chests_inner(string[CHESTS_SLICE:])

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        string, hash = split_chests_response(string)

        inner_string = cls.decode_inner(string)

        inner = ChestsInnerModel.from_robtop(inner_string)

        return cls(inner=inner, hash=hash)

    def to_robtop(self) -> str:
        return iter.of(self.encode_inner(), self.hash).collect(concat_chests_response)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return CHESTS_RESPONSE_SEPARATOR in string


decode_quests_inner = decode_robtop_string_with(Key.QUESTS)
encode_quests_inner = encode_robtop_string_with(Key.QUESTS)


@define()
class QuestsResponseModel(Model):
    inner: QuestsInnerModel = field(factory=QuestsInnerModel)
    hash: str = field()

    @hash.default
    def default_hash(self) -> str:
        return self.compute_hash()

    def compute_hash(self) -> str:
        return sha1_string_with_salt(self.encode_inner(), Salt.QUESTS)

    def encode_inner(self) -> str:
        return generate_random_string(QUESTS_SLICE) + encode_quests_inner(self.inner.to_robtop())

    @classmethod
    def decode_inner(cls, string: str) -> str:
        return decode_quests_inner(string[QUESTS_SLICE:])

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        inner_string, hash = split_quests_response(string)

        inner_string = cls.decode_inner(inner_string)

        inner = QuestsInnerModel.from_robtop(inner_string)

        return cls(inner=inner, hash=hash)

    def to_robtop(self) -> str:
        return iter.of(self.encode_inner(), self.hash).collect(concat_quests_response)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return QUESTS_RESPONSE_SEPARATOR in string


def gauntlet_to_robtop(gauntlet: GauntletModel) -> str:
    return gauntlet.to_robtop()


def gauntlet_hash_part(gauntlet: GauntletModel) -> str:
    return iter.of(
        str(gauntlet.id), iter(gauntlet.level_ids).map(str).collect(concat_level_ids)
    ).collect(concat_empty)


@define()
class GauntletsResponseModel(Model):
    gauntlets: List[GauntletModel] = field(factory=list)
    hash: str = field()

    @hash.default
    def default_hash(self) -> str:
        return self.compute_hash()

    def compute_hash(self) -> str:
        return sha1_string_with_salt(
            iter(self.gauntlets).map(gauntlet_hash_part).collect(concat_empty),
            Salt.LEVEL,
        )

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        gauntlets_string, hash = split_gauntlets_response(string)

        gauntlets = (
            iter(split_gauntlets_response_gauntlets(gauntlets_string))
            .map(GauntletModel.from_robtop)
            .list()
        )

        return cls(gauntlets=gauntlets, hash=hash)

    def to_robtop(self) -> str:
        return iter.of(
            iter(self.gauntlets)
            .map(gauntlet_to_robtop)
            .collect(concat_gauntlets_response_gauntlets),
            self.hash,
        ).collect(concat_gauntlets_response)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return GAUNTLETS_RESPONSE_SEPARATOR in string


def map_pack_to_robtop(map_pack: MapPackModel) -> str:
    return map_pack.to_robtop()


def map_packs_hash_part(map_pack: MapPackModel) -> str:
    string = str(map_pack.id)

    return iter.of(first(string), last(string), str(map_pack.stars), str(map_pack.coins)).collect(
        concat_empty
    )


@define()
class MapPacksResponseModel(Model):
    map_packs: List[MapPackModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)
    hash: str = field()

    @hash.default
    def default_hash(self) -> str:
        return self.compute_hash()

    def compute_hash(self) -> str:
        return sha1_string_with_salt(
            iter(self.map_packs).map(map_packs_hash_part).collect(concat_empty),
            Salt.LEVEL,
        )

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        map_packs_string, page_string, hash = split_map_packs_response(string)

        map_packs = (
            iter(split_map_packs_response_map_packs(map_packs_string))
            .map(MapPackModel.from_robtop)
            .list()
        )

        page = PageModel.from_robtop(page_string)

        return cls(map_packs=map_packs, page=page, hash=hash)

    def to_robtop(self) -> str:
        return iter.of(
            iter(self.map_packs)
            .map(map_pack_to_robtop)
            .collect(concat_map_packs_response_map_packs),
            self.page.to_robtop(),
            self.hash,
        ).collect(concat_map_packs_response)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return MAP_PACKS_RESPONSE_SEPARATOR in string


def level_leaderboard_user_to_robtop(
    level_leaderboard_user: LevelLeaderboardUserModel,
) -> str:
    return level_leaderboard_user.to_robtop()


@define()
class LevelLeaderboardResponseModel(Model):
    users: List[LevelLeaderboardUserModel] = field(factory=list)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        users = (
            iter(split_level_leaderboard_response_users(string))
            .map(LevelLeaderboardUserModel.from_robtop)
            .list()
        )

        return cls(users=users)

    def to_robtop(self) -> str:
        return (
            iter(self.users)
            .map(level_leaderboard_user_to_robtop)
            .collect(concat_level_leaderboard_response_users)
        )

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_LEADERBOARD_RESPONSE_USERS_SEPARATOR in string


def level_comment_to_robtop(level_comment: LevelCommentModel) -> str:
    return level_comment.to_robtop()


@define()
class LevelCommentsResponseModel(Model):
    comments: List[LevelCommentModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        comments_string, page_string = split_level_comments_response(string)

        comments = (
            iter(split_level_comments_response_comments(comments_string))
            .map(LevelCommentModel.from_robtop)
            .list()
        )

        page = PageModel.from_robtop(page_string)

        return cls(comments=comments, page=page)

    def to_robtop(self) -> str:
        return iter.of(
            iter(self.comments)
            .map(level_comment_to_robtop)
            .collect(concat_level_comments_response_comments),
            self.page.to_robtop(),
        ).collect(concat_level_comments_response)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_COMMENTS_RESPONSE_SEPARATOR in string


def user_comment_to_robtop(user_comment: UserCommentModel) -> str:
    return user_comment.to_robtop()


@define()
class UserCommentsResponseModel(Model):
    comments: List[UserCommentModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        comments_string, page_string = split_user_comments_response(string)

        comments = (
            iter(split_user_comments_response_comments(comments_string))
            .map(UserCommentModel.from_robtop)
            .list()
        )

        page = PageModel.from_robtop(page_string)

        return cls(comments=comments, page=page)

    def to_robtop(self) -> str:
        return iter.of(
            iter(self.comments)
            .map(user_comment_to_robtop)
            .collect(concat_user_comments_response_comments),
            self.page.to_robtop(),
        ).collect(concat_user_comments_response)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return USER_COMMENTS_RESPONSE_SEPARATOR in string


SMART_HASH_COUNT = 40


@define()
class LevelResponseModel:
    level: LevelModel = field(factory=LevelModel)
    smart_hash: str = field()  # *smart* hash
    hash: str = field()
    creator: Optional[CreatorModel] = field(default=None)

    @smart_hash.default
    def default_smart_hash(self) -> str:
        return self.compute_smart_hash()

    def compute_smart_hash(self) -> str:
        return sha1_string_with_salt(
            generate_level_seed(self.level.to_robtop(), SMART_HASH_COUNT), Salt.LEVEL
        )

    @hash.default
    def default_hash(self) -> str:
        return self.compute_hash()

    def compute_hash(self) -> str:
        return sha1_string_with_salt(self.level.to_robtop(), Salt.LEVEL)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
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

        if creator is None:
            return iter.of(self.level.to_robtop(), self.smart_hash, self.hash).collect(
                concat_level_response
            )

        else:
            return iter.of(
                self.level.to_robtop(), self.smart_hash, self.hash, creator.to_robtop()
            ).collect(concat_level_response)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_RESPONSE_SEPARATOR in string


def search_levels_hash_part(level: LevelModel) -> str:
    string = str(level.id)

    return iter.of(first(string), last(string), str(level.reward.count), str(level.coins)).collect(
        concat_empty
    )


@define()
class SearchLevelsResponseModel(Model):
    levels: List[LevelModel] = field(factory=list)
    creators: List[CreatorModel] = field(factory=list)
    songs: List[SongModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)
    hash: str = field()

    @hash.default
    def default_hash(self) -> str:
        return self.compute_hash()

    def compute_hash(self) -> str:
        return sha1_string_with_salt(
            iter(self.levels).map(search_levels_hash_part).collect(concat_empty),
            Salt.LEVEL,
        )

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        (
            levels_string,
            creators_string,
            songs_string,
            page_string,
            hash,
        ) = split_search_levels_response(string)

        levels = (
            iter(split_search_levels_response_levels(levels_string))
            .map(LevelModel.from_robtop)
            .list()
        )

        creators = (
            iter(split_search_levels_response_creators(creators_string))
            .map(CreatorModel.from_robtop)
            .list()
        )

        songs = (
            iter(split_search_levels_response_songs(songs_string)).map(SongModel.from_robtop).list()
        )

        page = PageModel.from_robtop(page_string)

        return cls(levels=levels, creators=creators, songs=songs, page=page, hash=hash)

    def to_robtop(self) -> str:
        return iter.of(
            concat_search_levels_response_levels(level.to_robtop() for level in self.levels),
            concat_search_levels_response_creators(
                creator.to_robtop() for creator in self.creators
            ),
            concat_search_levels_response_songs(song.to_robtop() for song in self.songs),
            self.page.to_robtop(),
            self.hash,
        ).collect(concat_search_levels_response)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return SEARCH_LEVELS_RESPONSE_SEPARATOR in string


def search_user_to_robtop(search_user: SearchUserModel) -> str:
    return search_user.to_robtop()


@define()
class SearchUsersResponseModel(Model):
    users: List[SearchUserModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        users_string, page_string = split_search_users_response(string)

        users = (
            iter(split_search_users_response_users(users_string))
            .map(SearchUserModel.from_robtop)
            .list()
        )

        page = PageModel.from_robtop(page_string)

        return cls(users=users, page=page)

    def to_robtop(self) -> str:
        return iter.of(
            iter(self.users).map(search_user_to_robtop).collect(concat_search_users_response_users),
            self.page.to_robtop(),
        ).collect(concat_search_users_response)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return SEARCH_USERS_RESPONSE_SEPARATOR in string


def relationship_user_to_robtop(relationship_user: RelationshipUserModel) -> str:
    return relationship_user.to_robtop()


@define()
class RelationshipsResponseModel(Model):
    users: List[RelationshipUserModel] = field(factory=list)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        users = (
            iter(split_relationships_response_users(string))
            .map(RelationshipUserModel.from_robtop)
            .list()
        )

        return cls(users=users)

    def to_robtop(self) -> str:
        return (
            iter(self.users)
            .map(relationship_user_to_robtop)
            .collect(concat_relationships_response_users)
        )

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return RELATIONSHIPS_RESPONSE_USERS_SEPARATOR in string


def leaderboard_user_to_robtop(leaderboard_user: LeaderboardUserModel) -> str:
    return leaderboard_user.to_robtop()


@define()
class LeaderboardResponseModel(Model):
    users: List[LeaderboardUserModel] = field(factory=list)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        users = (
            iter(split_leaderboard_response_users(string))
            .map(LeaderboardUserModel.from_robtop)
            .list()
        )

        return cls(users=users)

    def to_robtop(self) -> str:
        return (
            iter(self.users)
            .map(leaderboard_user_to_robtop)
            .collect(concat_leaderboard_response_users)
        )

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEADERBOARD_RESPONSE_USERS_SEPARATOR in string


def message_to_robtop(message: MessageModel) -> str:
    return message.to_robtop()


@define()
class MessagesResponseModel(Model):
    messages: List[MessageModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        messages_string, page_string = split_messages_response(string)

        messages = (
            iter(split_messages_response_messages(messages_string))
            .map(MessageModel.from_robtop)
            .list()
        )

        page = PageModel.from_robtop(page_string)

        return cls(messages=messages, page=page)

    def to_robtop(self) -> str:
        return iter.of(
            iter(self.messages).map(message_to_robtop).collect(concat_messages_response_messages),
            self.page.to_robtop(),
        ).collect(concat_messages_response)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return MESSAGES_RESPONSE_SEPARATOR in string


def artist_to_robtop(artist: ArtistModel) -> str:
    return artist.to_robtop()


@define()
class ArtistsResponseModel(Model):
    artists: List[ArtistModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        artists_string, page_string = split_artists_response(string)

        artists = (
            iter(split_artists_response_artists(artists_string)).map(ArtistModel.from_robtop).list()
        )

        page = PageModel.from_robtop(page_string)

        return cls(artists=artists, page=page)

    def to_robtop(self) -> str:
        return iter.of(
            iter(self.artists).map(artist_to_robtop).collect(concat_artists_response_artists),
            self.page.to_robtop(),
        ).collect(concat_artists_response)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return ARTISTS_RESPONSE_SEPARATOR in string


def friend_request_to_robtop(friend_request: FriendRequestModel) -> str:
    return friend_request.to_robtop()


@define()
class FriendRequestsResponseModel(Model):
    friend_requests: List[FriendRequestModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        friend_requests_string, page_string = split_friend_requests_response(string)

        friend_requests = (
            iter(split_friend_requests_response_friend_requests(friend_requests_string))
            .map(FriendRequestModel.from_robtop)
            .list()
        )

        page = PageModel.from_robtop(page_string)

        return cls(friend_requests=friend_requests, page=page)

    def to_robtop(self) -> str:
        return iter.of(
            iter(self.friend_requests)
            .map(friend_request_to_robtop)
            .collect(concat_friend_requests_response_friend_requests),
            self.page.to_robtop(),
        ).collect(concat_friend_requests_response)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return MESSAGES_RESPONSE_SEPARATOR in string


TEMPORARY = "temp"


@define()
class CommentBannedModel(Model):
    string: str = field(default=TEMPORARY)
    timeout: Duration = field(factory=duration)
    reason: str = field(default=EMPTY)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        string, timeout_string, reason = split_comment_banned(string)

        timeout_seconds = int(timeout_string)

        timeout = duration(seconds=timeout_seconds)

        return cls(string=string, timeout=timeout, reason=reason)

    def to_robtop(self) -> str:
        return iter.of(
            self.string,
            str(int(self.timeout.total_seconds())),
            self.reason,
        ).collect(concat_comment_banned)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return COMMENT_BANNED_SEPARATOR in string
