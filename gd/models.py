from typing import List, Optional, Sequence, Type, TypeVar
from urllib.parse import quote, unquote

from attrs import define, field
from iters.iters import iter
from pendulum import DateTime, Duration, duration
from typing_aliases import DynamicTuple
from typing_extensions import Protocol
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
    DEFAULT_CONTENT_PRESENT,
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
    DEFAULT_NEW,
    DEFAULT_NUMERATOR,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_ORBS,
    DEFAULT_PLACE,
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
    DEFAULT_TWO_PLAYER,
    DEFAULT_UNREAD,
    DEFAULT_USER_COINS,
    DEFAULT_VERIFIED_COINS,
    DEFAULT_VERSION,
    EMPTY,
    QUESTS_SLICE,
    WEEKLY_ID_ADD,
)
from gd.date_time import date_time_from_human, date_time_to_human, utc_now
from gd.decorators import cache_by
from gd.difficulty_parameters import DEFAULT_DEMON_DIFFICULTY_VALUE, DifficultyParameters
from gd.encoding import (
    decode_base64_string_url_safe,
    decode_robtop_string,
    encode_base64_string_url_safe,
    encode_robtop_string,
    generate_level_seed,
    generate_random_string,
    sha1_string_with_salt,
    unzip_level_string,
    zip_level_string,
)
from gd.enums import (
    CommentState,
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
    OBJECTS_SEPARATOR,
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
    parse_get_or,
    parse_get_or_else,
    partial_parse_enum,
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
from gd.string_utils import concat_empty
from gd.versions import CURRENT_GAME_VERSION, GameVersion

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
SONG_DOWNLOAD_URL = 10


S = TypeVar("S", bound="SongModel")


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
    download_url: Optional[URL] = None

    @classmethod
    def from_robtop(
        cls: Type[S], string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
    ) -> S:
        mapping = split_song(string)

        id = parse_get_or(int, DEFAULT_ID, mapping.get(SONG_ID))

        name = mapping.get(SONG_NAME, EMPTY)

        artist_name = mapping.get(SONG_ARTIST_NAME, EMPTY)

        artist_id = parse_get_or(int, DEFAULT_ID, mapping.get(SONG_ARTIST_ID))

        size = parse_get_or(float, DEFAULT_SIZE, mapping.get(SONG_SIZE))

        youtube_video_id = mapping.get(SONG_YOUTUBE_VIDEO_ID, EMPTY)
        youtube_channel_id = mapping.get(SONG_YOUTUBE_CHANNEL_ID, EMPTY)

        artist_verified = parse_get_or(
            int_bool, DEFAULT_ARTIST_VERIFIED, mapping.get(SONG_ARTIST_VERIFIED)
        )

        download_url_option = mapping.get(SONG_DOWNLOAD_URL)

        download_url = URL(unquote(download_url_option)) if download_url_option else None

        return cls(
            id=id,
            name=name,
            artist_name=artist_name,
            artist_id=artist_id,
            size=size,
            youtube_video_id=youtube_video_id,
            youtube_channel_id=youtube_channel_id,
            artist_verified=artist_verified,
            download_url=download_url,
        )

    def to_robtop(self) -> str:
        download_url = self.download_url

        mapping = {
            SONG_ID: str(self.id),
            SONG_NAME: self.name,
            SONG_ARTIST_NAME: self.artist_name,
            SONG_ARTIST_ID: str(self.artist_id),
            SONG_SIZE: float_str(self.size),
            SONG_YOUTUBE_VIDEO_ID: self.youtube_video_id,
            SONG_YOUTUBE_CHANNEL_ID: self.youtube_channel_id,
            SONG_ARTIST_VERIFIED: bool_str(self.is_artist_verified()),
            SONG_DOWNLOAD_URL: EMPTY if download_url else quote(str(download_url)),
        }

        return concat_song(mapping)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return SONG_SEPARATOR in string

    def is_artist_verified(self) -> bool:
        return self.artist_verified


LG = TypeVar("LG", bound="LoginModel")


@define()
class LoginModel(Model):
    account_id: int = DEFAULT_ID
    id: int = DEFAULT_ID

    @classmethod
    def from_robtop(cls: Type[LG], string: str) -> LG:
        account_id, id = iter(split_login(string)).map(int).tuple()

        return cls(account_id=account_id, id=id)

    def to_robtop(self) -> str:
        return iter.of(str(self.account_id), str(self.id)).collect(concat_login)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return LOGIN_SEPARATOR in string


CRT = TypeVar("CRT", bound="CreatorModel")


@define()
class CreatorModel(Model):
    id: int = DEFAULT_ID
    name: str = EMPTY
    account_id: int = DEFAULT_ID

    @classmethod
    def from_robtop(cls: Type[CRT], string: str) -> CRT:
        id_string, name, account_id_string = split_creator(string)

        id = int(id_string)

        account_id = int(account_id_string)

        return cls(id=id, name=name, account_id=account_id)

    def to_robtop(self) -> str:
        return iter.of(str(self.id), self.name, str(self.account_id)).collect(concat_creator)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return CREATOR_SEPARATOR in string


DEFAULT_START = 0
DEFAULT_STOP = 0


B = TypeVar("B", bound="PageModel")


@define()
class PageModel(Model):
    total: Optional[int] = None
    start: int = DEFAULT_START
    stop: int = DEFAULT_STOP

    @classmethod
    def from_robtop(cls: Type[B], string: str) -> B:
        total_string, start_string, stop_string = split_page(string)

        if not total_string:
            total = None

        else:
            total = int(total_string)

        start = int(start_string)
        stop = int(stop_string)

        return cls(total=total, start=start, stop=stop)

    def to_robtop(self) -> str:
        total = self.total
        start = self.start
        stop = self.stop

        if total is None:
            return iter.of(EMPTY, str(start), str(stop)).collect(concat_page)

        return iter.of(str(total), str(start), str(stop)).collect(concat_page)

    @staticmethod
    def can_be_in(string: str) -> bool:
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


SU = TypeVar("SU", bound="SearchUserModel")


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

    @classmethod
    def from_robtop(cls: Type[SU], string: str) -> SU:
        mapping = split_search_user(string)

        name = mapping.get(SEARCH_USER_NAME, EMPTY)

        id = parse_get_or(int, DEFAULT_ID, mapping.get(SEARCH_USER_ID))

        stars = parse_get_or(int, DEFAULT_STARS, mapping.get(SEARCH_USER_STARS))

        demons = parse_get_or(int, DEFAULT_DEMONS, mapping.get(SEARCH_USER_DEMONS))

        rank_option = mapping.get(SEARCH_USER_RANK)

        if rank_option:
            rank = int(rank_option)

        else:
            rank = DEFAULT_RANK

        creator_points = parse_get_or(
            int,
            DEFAULT_CREATOR_POINTS,
            mapping.get(SEARCH_USER_CREATOR_POINTS),
        )

        icon_id = parse_get_or(int, DEFAULT_ID, mapping.get(SEARCH_USER_ICON_ID))

        color_1_id = parse_get_or(int, DEFAULT_COLOR_1_ID, mapping.get(SEARCH_USER_COLOR_1_ID))
        color_2_id = parse_get_or(int, DEFAULT_COLOR_2_ID, mapping.get(SEARCH_USER_COLOR_2_ID))

        secret_coins = parse_get_or(
            int, DEFAULT_SECRET_COINS, mapping.get(SEARCH_USER_SECRET_COINS)
        )

        icon_type = parse_get_or(
            partial_parse_enum(int, IconType),
            IconType.DEFAULT,
            mapping.get(SEARCH_USER_ICON_TYPE),
        )

        glow = parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(SEARCH_USER_GLOW))

        account_id = parse_get_or(int, DEFAULT_ID, mapping.get(SEARCH_USER_ACCOUNT_ID))

        user_coins = parse_get_or(int, DEFAULT_USER_COINS, mapping.get(SEARCH_USER_USER_COINS))

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
        }

        return concat_search_user(mapping)

    @staticmethod
    def can_be_in(string: str) -> bool:
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
PROFILE_TWITTER = 44
PROFILE_TWITCH = 45
PROFILE_DIAMONDS = 46
PROFILE_EXPLOSION_ID = 48
PROFILE_ROLE_ID = 49
PROFILE_COMMENT_STATE = 50


P = TypeVar("P", bound="ProfileModel")


@define()
class ProfileModel(Model):
    name: str = EMPTY
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
    role_id: int = DEFAULT_ID
    comment_state: CommentState = CommentState.DEFAULT

    @classmethod
    def from_robtop(cls: Type[P], string: str) -> P:
        mapping = split_profile(string)

        name = mapping.get(PROFILE_NAME, EMPTY)

        id = parse_get_or(int, DEFAULT_ID, mapping.get(PROFILE_ID))

        stars = parse_get_or(int, DEFAULT_STARS, mapping.get(PROFILE_STARS))

        demons = parse_get_or(int, DEFAULT_DEMONS, mapping.get(PROFILE_DEMONS))

        creator_points = parse_get_or(
            int, DEFAULT_CREATOR_POINTS, mapping.get(PROFILE_CREATOR_POINTS)
        )

        color_1_id = parse_get_or(int, DEFAULT_COLOR_1_ID, mapping.get(PROFILE_COLOR_1_ID))
        color_2_id = parse_get_or(int, DEFAULT_COLOR_2_ID, mapping.get(PROFILE_COLOR_2_ID))

        secret_coins = parse_get_or(int, DEFAULT_SECRET_COINS, mapping.get(PROFILE_SECRET_COINS))

        account_id = parse_get_or(int, DEFAULT_ID, mapping.get(PROFILE_ACCOUNT_ID))

        user_coins = parse_get_or(int, DEFAULT_USER_COINS, mapping.get(PROFILE_USER_COINS))

        message_state = parse_get_or(
            partial_parse_enum(int, MessageState),
            MessageState.DEFAULT,
            mapping.get(PROFILE_MESSAGE_STATE),
        )

        friend_request_state = parse_get_or(
            partial_parse_enum(int, FriendRequestState),
            FriendRequestState.DEFAULT,
            mapping.get(PROFILE_FRIEND_REQUEST_STATE),
        )

        youtube = mapping.get(PROFILE_YOUTUBE) or None

        cube_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_CUBE_ID))
        ship_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_SHIP_ID))
        ball_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_BALL_ID))
        ufo_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_UFO_ID))
        wave_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_WAVE_ID))
        robot_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_ROBOT_ID))

        glow = parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(PROFILE_GLOW))

        active = parse_get_or(int_bool, DEFAULT_ACTIVE, mapping.get(PROFILE_ACTIVE))

        rank = parse_get_or(int, DEFAULT_RANK, mapping.get(PROFILE_RANK))

        friend_state = parse_get_or(
            partial_parse_enum(int, FriendState),
            FriendState.DEFAULT,
            mapping.get(PROFILE_FRIEND_STATE),
        )

        new_messages = parse_get_or(int, DEFAULT_NEW, mapping.get(PROFILE_NEW_MESSAGES))
        new_friend_requests = parse_get_or(
            int, DEFAULT_NEW, mapping.get(PROFILE_NEW_FRIEND_REQUESTS)
        )
        new_friends = parse_get_or(int, DEFAULT_NEW, mapping.get(PROFILE_NEW_FRIENDS))

        spider_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_SPIDER_ID))

        twitter = mapping.get(PROFILE_TWITTER) or None

        twitch = mapping.get(PROFILE_TWITCH) or None

        diamonds = parse_get_or(int, DEFAULT_DIAMONDS, mapping.get(PROFILE_DIAMONDS))

        explosion_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_EXPLOSION_ID))

        role_id = parse_get_or(int, DEFAULT_ID, mapping.get(PROFILE_ROLE_ID))

        comment_state = parse_get_or(
            partial_parse_enum(int, CommentState),
            CommentState.DEFAULT,
            mapping.get(PROFILE_COMMENT_STATE),
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
            twitter=twitter,
            twitch=twitch,
            diamonds=diamonds,
            explosion_id=explosion_id,
            role_id=role_id,
            comment_state=comment_state,
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
            PROFILE_TWITTER: self.twitter or EMPTY,
            PROFILE_TWITCH: self.twitch or EMPTY,
            PROFILE_DIAMONDS: str(self.diamonds),
            PROFILE_EXPLOSION_ID: str(self.explosion_id),
            PROFILE_ROLE_ID: str(self.role_id),
            PROFILE_COMMENT_STATE: str(self.comment_state.value),
        }

        return concat_profile(mapping)

    @staticmethod
    def can_be_in(string: str) -> bool:
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


RU = TypeVar("RU", bound="RelationshipUserModel")


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
    def from_robtop(cls: Type[RU], string: str) -> RU:
        mapping = split_relationship_user(string)

        name = mapping.get(RELATIONSHIP_USER_NAME, EMPTY)

        id = parse_get_or(int, DEFAULT_ID, mapping.get(RELATIONSHIP_USER_ID))

        icon_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(RELATIONSHIP_USER_ICON_ID))

        color_1_id = parse_get_or(
            int, DEFAULT_COLOR_1_ID, mapping.get(RELATIONSHIP_USER_COLOR_1_ID)
        )
        color_2_id = parse_get_or(
            int, DEFAULT_COLOR_2_ID, mapping.get(RELATIONSHIP_USER_COLOR_2_ID)
        )

        icon_type = parse_get_or(
            partial_parse_enum(int, IconType),
            IconType.DEFAULT,
            mapping.get(RELATIONSHIP_USER_ICON_TYPE),
        )

        glow = parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(RELATIONSHIP_USER_GLOW))

        account_id = parse_get_or(int, DEFAULT_ID, mapping.get(RELATIONSHIP_USER_ACCOUNT_ID))

        message_state = parse_get_or(
            partial_parse_enum(int, MessageState),
            MessageState.DEFAULT,
            mapping.get(RELATIONSHIP_USER_MESSAGE_STATE),
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

    @staticmethod
    def can_be_in(string: str) -> bool:
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


LU = TypeVar("LU", bound="LeaderboardUserModel")


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

    @classmethod
    def from_robtop(cls: Type[LU], string: str) -> LU:
        mapping = split_leaderboard_user(string)

        name = mapping.get(LEADERBOARD_USER_NAME, EMPTY)

        id = parse_get_or(int, DEFAULT_ID, mapping.get(LEADERBOARD_USER_ID))

        stars = parse_get_or(int, DEFAULT_STARS, mapping.get(LEADERBOARD_USER_STARS))

        demons = parse_get_or(int, DEFAULT_DEMONS, mapping.get(LEADERBOARD_USER_DEMONS))

        place = parse_get_or(int, DEFAULT_PLACE, mapping.get(LEADERBOARD_USER_PLACE))

        creator_points = parse_get_or(
            int, DEFAULT_CREATOR_POINTS, mapping.get(LEADERBOARD_USER_CREATOR_POINTS)
        )

        icon_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(LEADERBOARD_USER_ICON_ID))

        color_1_id = parse_get_or(int, DEFAULT_COLOR_1_ID, mapping.get(LEADERBOARD_USER_COLOR_1_ID))
        color_2_id = parse_get_or(int, DEFAULT_COLOR_2_ID, mapping.get(LEADERBOARD_USER_COLOR_2_ID))

        secret_coins = parse_get_or(
            int, DEFAULT_SECRET_COINS, mapping.get(LEADERBOARD_USER_SECRET_COINS)
        )

        icon_type = parse_get_or(
            partial_parse_enum(int, IconType),
            IconType.DEFAULT,
            mapping.get(LEADERBOARD_USER_ICON_TYPE),
        )

        glow = parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(LEADERBOARD_USER_GLOW))

        account_id = parse_get_or(int, DEFAULT_ID, mapping.get(LEADERBOARD_USER_ACCOUNT_ID))

        user_coins = parse_get_or(int, DEFAULT_USER_COINS, mapping.get(LEADERBOARD_USER_USER_COINS))

        diamonds = parse_get_or(int, DEFAULT_DIAMONDS, mapping.get(LEADERBOARD_USER_DIAMONDS))

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
        }

        return concat_leaderboard_user(mapping)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return LEADERBOARD_USER_SEPARATOR in string

    def has_glow(self) -> bool:
        return self.glow


TI = TypeVar("TI", bound="TimelyInfoModel")


@define()
class TimelyInfoModel(Model):
    id: int = field(default=DEFAULT_ID)
    type: TimelyType = field(default=TimelyType.DEFAULT)
    cooldown: Duration = field(factory=duration)

    @classmethod
    def from_robtop(cls: Type[TI], string: str, type: TimelyType = TimelyType.DEFAULT) -> TI:
        id, cooldown_seconds = iter(split_timely_info(string)).map(int).tuple()

        id %= WEEKLY_ID_ADD

        cooldown = duration(seconds=cooldown_seconds)

        return cls(id=id, type=type, cooldown=cooldown)

    def to_robtop(self) -> str:
        id = self.id

        if self.type.is_weekly():
            id += WEEKLY_ID_ADD

        return iter.of(str(id), str(int(self.cooldown.total_seconds()))).collect(  # type: ignore
            concat_timely_info
        )

    @staticmethod
    def can_be_in(string: str) -> bool:
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
    name: str = field(default=EMPTY)
    created_at: DateTime = field(factory=utc_now)
    read: bool = field(default=DEFAULT_READ)
    sent: bool = field(default=DEFAULT_SENT)

    content_present: bool = field(default=DEFAULT_CONTENT_PRESENT)

    @classmethod
    def from_robtop(
        cls: Type[M], string: str, content_present: bool = DEFAULT_CONTENT_PRESENT
    ) -> M:
        mapping = split_message(string)

        id = parse_get_or(int, DEFAULT_ID, mapping.get(MESSAGE_ID))

        account_id = parse_get_or(int, DEFAULT_ID, mapping.get(MESSAGE_ACCOUNT_ID))
        user_id = parse_get_or(
            int,
            DEFAULT_ID,
            mapping.get(MESSAGE_USER_ID),
        )

        subject = decode_base64_string_url_safe(mapping.get(MESSAGE_SUBJECT, EMPTY))

        content = decode_robtop_string(mapping.get(MESSAGE_CONTENT, EMPTY), Key.MESSAGE)

        name = mapping.get(MESSAGE_NAME, EMPTY)

        created_at = parse_get_or_else(
            date_time_from_human, utc_now, mapping.get(MESSAGE_CREATED_AT), ignore_errors=True
        )

        read = parse_get_or(int_bool, DEFAULT_READ, mapping.get(MESSAGE_READ))

        sent = parse_get_or(int_bool, DEFAULT_SENT, mapping.get(MESSAGE_SENT))

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
            MESSAGE_CONTENT: encode_robtop_string(self.content, Key.MESSAGE),
            MESSAGE_NAME: self.name,
            MESSAGE_CREATED_AT: date_time_to_human(self.created_at),
            MESSAGE_READ: bool_str(self.is_read()),
            MESSAGE_SENT: bool_str(self.is_sent()),
        }

        return concat_message(mapping)

    @staticmethod
    def can_be_in(string: str) -> bool:
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


FR = TypeVar("FR", bound="FriendRequestModel")


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
    def from_robtop(cls: Type[FR], string: str) -> FR:
        mapping = split_friend_request(string)

        name = mapping.get(FRIEND_REQUEST_NAME, EMPTY)

        user_id = parse_get_or(int, DEFAULT_ID, mapping.get(FRIEND_REQUEST_USER_ID))

        icon_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(FRIEND_REQUEST_ICON_ID))

        color_1_id = parse_get_or(int, DEFAULT_COLOR_1_ID, mapping.get(FRIEND_REQUEST_COLOR_1_ID))
        color_2_id = parse_get_or(int, DEFAULT_COLOR_2_ID, mapping.get(FRIEND_REQUEST_COLOR_2_ID))

        icon_type = parse_get_or(
            partial_parse_enum(int, IconType),
            IconType.DEFAULT,
            mapping.get(FRIEND_REQUEST_ICON_TYPE),
        )

        glow = parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(FRIEND_REQUEST_GLOW))

        account_id = parse_get_or(int, DEFAULT_ID, mapping.get(FRIEND_REQUEST_ACCOUNT_ID))

        id = parse_get_or(int, DEFAULT_ID, mapping.get(FRIEND_REQUEST_ID))

        content = decode_base64_string_url_safe(mapping.get(FRIEND_REQUEST_CONTENT, EMPTY))

        created_at = parse_get_or_else(
            date_time_from_human,
            utc_now,
            mapping.get(FRIEND_REQUEST_CREATED_AT),
            ignore_errors=True,
        )

        unread = parse_get_or(int_bool, DEFAULT_UNREAD, mapping.get(FRIEND_REQUEST_UNREAD))

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

    @staticmethod
    def can_be_in(string: str) -> bool:
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
LEVEL_STARS = 18
LEVEL_SCORE = 19
LEVEL_AUTO = 25
LEVEL_PASSWORD_DATA = 27
LEVEL_CREATED_AT = 28
LEVEL_UPDATED_AT = 29
LEVEL_ORIGINAL_ID = 30
LEVEL_TWO_PLAYER = 31
LEVEL_CUSTOM_SONG_ID = 35
LEVEL_CAPACITY = 36
LEVEL_COINS = 37
LEVEL_VERIFIED_COINS = 38
LEVEL_REQUESTED_STARS = 39
LEVEL_LOW_DETAIL = 40
LEVEL_TIMELY_ID = 41
LEVEL_SPECIAL_RATE_TYPE = 42
LEVEL_DEMON_DIFFICULTY = 43
LEVEL_OBJECT_COUNT = 45
LEVEL_EDITOR_TIME = 46
LEVEL_COPIES_TIME = 47

UNPROCESSED_DATA = "unprocessed_data"


L = TypeVar("L", bound="LevelModel")


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
    stars: int = field(default=DEFAULT_STARS)
    score: int = field(default=DEFAULT_SCORE)
    password_data: Password = field(factory=Password)
    created_at: DateTime = field(factory=utc_now)
    updated_at: DateTime = field(factory=utc_now)
    original_id: int = field(default=DEFAULT_ID)
    two_player: bool = field(default=DEFAULT_TWO_PLAYER)
    custom_song_id: int = field(default=DEFAULT_ID)
    capacity: Capacity = field(factory=Capacity)
    coins: int = field(default=DEFAULT_COINS)
    verified_coins: bool = field(default=DEFAULT_VERIFIED_COINS)
    requested_stars: int = field(default=DEFAULT_STARS)
    low_detail: bool = field(default=DEFAULT_LOW_DETAIL)
    timely_id: int = field(default=DEFAULT_ID)
    timely_type: TimelyType = field(default=TimelyType.DEFAULT)
    special_rate_type: SpecialRateType = field(default=SpecialRateType.DEFAULT)
    object_count: int = field(default=DEFAULT_OBJECT_COUNT)
    editor_time: Duration = field(factory=duration)
    copies_time: Duration = field(factory=duration)

    @classmethod
    def from_robtop(cls: Type[L], string: str) -> L:
        mapping = split_level(string)

        id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_ID))

        name = mapping.get(LEVEL_NAME, EMPTY)

        description = decode_base64_string_url_safe(mapping.get(LEVEL_DESCRIPTION, EMPTY))

        unprocessed_data = mapping.get(LEVEL_UNPROCESSED_DATA, EMPTY)

        if OBJECTS_SEPARATOR in unprocessed_data:
            unprocessed_data = zip_level_string(unprocessed_data)

        version = parse_get_or(int, DEFAULT_VERSION, mapping.get(LEVEL_VERSION))

        creator_id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_CREATOR_ID))

        difficulty_numerator = parse_get_or(
            int, DEFAULT_NUMERATOR, mapping.get(LEVEL_DIFFICULTY_NUMERATOR)
        )

        difficulty_denominator = parse_get_or(
            int, DEFAULT_DENOMINATOR, mapping.get(LEVEL_DIFFICULTY_DENOMINATOR)
        )

        demon_difficulty_value = parse_get_or(
            int, DEFAULT_DEMON_DIFFICULTY_VALUE, mapping.get(LEVEL_DEMON_DIFFICULTY)
        )

        auto = parse_get_or(int_bool, DEFAULT_AUTO, mapping.get(LEVEL_AUTO))
        demon = parse_get_or(int_bool, DEFAULT_DEMON, mapping.get(LEVEL_DEMON))

        difficulty = DifficultyParameters(
            difficulty_numerator=difficulty_numerator,
            difficulty_denominator=difficulty_denominator,
            demon_difficulty_value=demon_difficulty_value,
            auto=auto,
            demon=demon,
        ).into_difficulty()

        downloads = parse_get_or(int, DEFAULT_DOWNLOADS, mapping.get(LEVEL_DOWNLOADS))

        official_song_id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_OFFICIAL_SONG_ID))

        game_version = parse_get_or(
            GameVersion.from_robtop, CURRENT_GAME_VERSION, mapping.get(LEVEL_GAME_VERSION)
        )

        rating = parse_get_or(int, DEFAULT_RATING, mapping.get(LEVEL_RATING))

        length = parse_get_or(
            partial_parse_enum(int, LevelLength),
            LevelLength.DEFAULT,
            mapping.get(LEVEL_LENGTH),
        )

        stars = parse_get_or(int, DEFAULT_STARS, mapping.get(LEVEL_STARS))

        score = parse_get_or(int, DEFAULT_SCORE, mapping.get(LEVEL_SCORE))

        if score < 0:
            score = 0

        password_data = parse_get_or_else(
            Password.from_robtop, Password, mapping.get(LEVEL_PASSWORD_DATA)
        )

        created_at = parse_get_or_else(
            date_time_from_human,
            utc_now,
            mapping.get(LEVEL_CREATED_AT),
            ignore_errors=True,
        )

        updated_at = parse_get_or_else(
            date_time_from_human,
            utc_now,
            mapping.get(LEVEL_UPDATED_AT),
            ignore_errors=True,
        )

        original_id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_ORIGINAL_ID))

        two_player = parse_get_or(int_bool, DEFAULT_TWO_PLAYER, mapping.get(LEVEL_TWO_PLAYER))

        custom_song_id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_CUSTOM_SONG_ID))

        capacity = parse_get_or_else(Capacity.from_robtop, Capacity, mapping.get(LEVEL_CAPACITY))

        coins = parse_get_or(int, DEFAULT_COINS, mapping.get(LEVEL_COINS))

        verified_coins = parse_get_or(
            int_bool, DEFAULT_VERIFIED_COINS, mapping.get(LEVEL_VERIFIED_COINS)
        )

        requested_stars = parse_get_or(int, DEFAULT_STARS, mapping.get(LEVEL_REQUESTED_STARS))

        low_detail = parse_get_or(int_bool, DEFAULT_LOW_DETAIL, mapping.get(LEVEL_LOW_DETAIL))

        timely_id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_TIMELY_ID))

        if timely_id:
            result, timely_id = divmod(timely_id, WEEKLY_ID_ADD)

            if result:
                timely_type = TimelyType.WEEKLY

            else:
                timely_type = TimelyType.DAILY

        else:
            timely_type = TimelyType.NOT_TIMELY

        special_rate_type = parse_get_or(
            partial_parse_enum(int, SpecialRateType),
            SpecialRateType.DEFAULT,
            mapping.get(LEVEL_SPECIAL_RATE_TYPE),
        )

        object_count = parse_get_or(int, DEFAULT_OBJECT_COUNT, mapping.get(LEVEL_OBJECT_COUNT))

        editor_seconds_option = mapping.get(LEVEL_EDITOR_TIME)

        if editor_seconds_option:
            editor_seconds = int(editor_seconds_option)
            editor_time = duration(seconds=editor_seconds)

        else:
            editor_time = duration()

        copies_seconds_option = mapping.get(LEVEL_COPIES_TIME)

        if copies_seconds_option:
            copies_seconds = int(copies_seconds_option)
            copies_time = duration(seconds=copies_seconds)

        else:
            copies_time = duration()

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
            stars=stars,
            score=score,
            password_data=password_data,
            created_at=created_at,
            updated_at=updated_at,
            original_id=original_id,
            two_player=two_player,
            custom_song_id=custom_song_id,
            capacity=capacity,
            coins=coins,
            verified_coins=verified_coins,
            requested_stars=requested_stars,
            low_detail=low_detail,
            timely_id=timely_id,
            timely_type=timely_type,
            special_rate_type=special_rate_type,
            object_count=object_count,
            editor_time=editor_time,
            copies_time=copies_time,
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
            LEVEL_STARS: str(self.stars),
            LEVEL_SCORE: str(self.score),
            LEVEL_AUTO: auto_string,
            LEVEL_PASSWORD_DATA: self.password_data.to_robtop(),
            LEVEL_CREATED_AT: date_time_to_human(self.created_at),
            LEVEL_UPDATED_AT: date_time_to_human(self.updated_at),
            LEVEL_ORIGINAL_ID: str(self.original_id),
            LEVEL_TWO_PLAYER: two_player_string,
            LEVEL_CUSTOM_SONG_ID: str(self.custom_song_id),
            LEVEL_CAPACITY: self.capacity.to_robtop(),
            LEVEL_COINS: str(self.coins),
            LEVEL_VERIFIED_COINS: bool_str(self.has_verified_coins()),
            LEVEL_REQUESTED_STARS: str(self.requested_stars),
            LEVEL_LOW_DETAIL: bool_str(self.has_low_detail()),
            LEVEL_TIMELY_ID: str(timely_id),
            LEVEL_SPECIAL_RATE_TYPE: str(self.special_rate_type.value),
            LEVEL_DEMON_DIFFICULTY: str(difficulty_parameters.demon_difficulty_value),
            LEVEL_OBJECT_COUNT: str(self.object_count),
            LEVEL_EDITOR_TIME: str(int(self.editor_time.total_seconds())),  # type: ignore
            LEVEL_COPIES_TIME: str(int(self.copies_time.total_seconds())),  # type: ignore
        }

        return concat_level(mapping)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return LEVEL_SEPARATOR in string

    def is_two_player(self) -> bool:
        return self.two_player

    def has_low_detail(self) -> bool:
        return self.low_detail

    def is_epic(self) -> bool:
        return self.special_rate_type.is_epic()

    def is_godlike(self) -> bool:
        return self.special_rate_type.is_godlike()

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


LCI = TypeVar("LCI", bound="LevelCommentInnerModel")


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
    def from_robtop(cls: Type[LCI], string: str) -> LCI:
        mapping = split_level_comment_inner(string)

        level_id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_COMMENT_INNER_LEVEL_ID))

        content = decode_base64_string_url_safe(mapping.get(LEVEL_COMMENT_INNER_CONTENT, EMPTY))

        user_id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_COMMENT_INNER_USER_ID))

        rating = parse_get_or(int, DEFAULT_RATING, mapping.get(LEVEL_COMMENT_INNER_RATING))

        id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_COMMENT_INNER_ID))

        spam = parse_get_or(int_bool, DEFAULT_SPAM, mapping.get(LEVEL_COMMENT_INNER_SPAM))

        created_at = parse_get_or_else(
            date_time_from_human,
            utc_now,
            mapping.get(LEVEL_COMMENT_INNER_CREATED_AT),
            ignore_errors=True,
        )

        record = parse_get_or(int, DEFAULT_RECORD, mapping.get(LEVEL_COMMENT_INNER_RECORD))

        role_id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_COMMENT_INNER_ROLE_ID))

        color = parse_get_or_else(
            Color.from_robtop, Color.default, mapping.get(LEVEL_COMMENT_INNER_COLOR)
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

    @staticmethod
    def can_be_in(string: str) -> bool:
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
    name: str = EMPTY
    icon_id: int = DEFAULT_ICON_ID
    color_1_id: int = DEFAULT_COLOR_1_ID
    color_2_id: int = DEFAULT_COLOR_2_ID
    icon_type: IconType = IconType.DEFAULT
    glow: bool = DEFAULT_GLOW
    account_id: int = DEFAULT_ID

    @classmethod
    def from_robtop(cls: Type[LCU], string: str) -> LCU:
        mapping = split_level_comment_user(string)

        name = mapping.get(LEVEL_COMMENT_USER_NAME, EMPTY)

        icon_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(LEVEL_COMMENT_USER_ICON_ID))

        color_1_id = parse_get_or(
            int, DEFAULT_COLOR_1_ID, mapping.get(LEVEL_COMMENT_USER_COLOR_1_ID)
        )
        color_2_id = parse_get_or(
            int, DEFAULT_COLOR_2_ID, mapping.get(LEVEL_COMMENT_USER_COLOR_2_ID)
        )

        icon_type = parse_get_or(
            partial_parse_enum(int, IconType),
            IconType.DEFAULT,
            mapping.get(LEVEL_COMMENT_USER_ICON_TYPE),
        )

        glow = parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(LEVEL_COMMENT_USER_GLOW))

        account_id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_COMMENT_USER_ACCOUNT_ID))

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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return LEVEL_COMMENT_USER_SEPARATOR in string

    def has_glow(self) -> bool:
        return self.glow


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
        return iter.of(self.inner.to_robtop(), self.user.to_robtop()).collect(concat_level_comment)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return LEVEL_COMMENT_SEPARATOR in string


USER_COMMENT_CONTENT = 2
USER_COMMENT_RATING = 4
USER_COMMENT_ID = 6
USER_COMMENT_CREATED_AT = 9


UC = TypeVar("UC", bound="UserCommentModel")


@define()
class UserCommentModel(Model):
    content: str = field(default=EMPTY)
    rating: int = field(default=DEFAULT_RATING)
    id: int = field(default=DEFAULT_ID)
    created_at: DateTime = field(factory=utc_now)

    @classmethod
    def from_robtop(cls: Type[UC], string: str) -> UC:
        mapping = split_user_comment(string)

        content = decode_base64_string_url_safe(mapping.get(USER_COMMENT_CONTENT, EMPTY))

        rating = parse_get_or(int, DEFAULT_RATING, mapping.get(USER_COMMENT_RATING))

        id = parse_get_or(int, DEFAULT_ID, mapping.get(USER_COMMENT_ID))

        created_at = parse_get_or_else(
            date_time_from_human,
            utc_now,
            mapping.get(USER_COMMENT_CREATED_AT),
            ignore_errors=True,
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

    @staticmethod
    def can_be_in(string: str) -> bool:
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
    name: str = field(default=EMPTY)
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
    def from_robtop(cls: Type[LLU], string: str) -> LLU:
        mapping = split_level_leaderboard_user(string)

        name = mapping.get(LEVEL_LEADERBOARD_USER_NAME, EMPTY)

        id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_LEADERBOARD_USER_ID))

        record = parse_get_or(int, DEFAULT_RECORD, mapping.get(LEVEL_LEADERBOARD_USER_RECORD))

        place = parse_get_or(int, DEFAULT_PLACE, mapping.get(LEVEL_LEADERBOARD_USER_PLACE))

        icon_id = parse_get_or(int, DEFAULT_ICON_ID, mapping.get(LEVEL_LEADERBOARD_USER_ICON_ID))

        color_1_id = parse_get_or(
            int, DEFAULT_COLOR_1_ID, mapping.get(LEVEL_LEADERBOARD_USER_COLOR_1_ID)
        )
        color_2_id = parse_get_or(
            int, DEFAULT_COLOR_2_ID, mapping.get(LEVEL_LEADERBOARD_USER_COLOR_2_ID)
        )

        coins = parse_get_or(int, DEFAULT_COINS, mapping.get(LEVEL_LEADERBOARD_USER_COINS))

        icon_type = parse_get_or(
            partial_parse_enum(int, IconType),
            IconType.DEFAULT,
            mapping.get(LEVEL_LEADERBOARD_USER_ICON_TYPE),
        )

        glow = parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(LEVEL_LEADERBOARD_USER_GLOW))

        recorded_at = parse_get_or_else(
            date_time_from_human,
            utc_now,
            mapping.get(LEVEL_LEADERBOARD_USER_RECORDED_AT),
            ignore_errors=True,
        )

        return cls(
            name=name,
            id=id,
            record=record,
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
            LEVEL_LEADERBOARD_USER_RECORD: str(self.record),
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return LEVEL_LEADERBOARD_USER_SEPARATOR in string

    def has_glow(self) -> bool:
        return self.glow


ARTIST_NAME = 4


A = TypeVar("A", bound="ArtistModel")


@define()
class ArtistModel(Model):
    name: str = EMPTY

    @classmethod
    def from_robtop(cls: Type[A], string: str) -> A:
        mapping = split_artist(string)

        name = mapping.get(ARTIST_NAME, EMPTY)

        return cls(name=name)

    def to_robtop(self) -> str:
        mapping = {ARTIST_NAME: self.name}

        return concat_artist(mapping)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return ARTIST_SEPARATOR in string


C = TypeVar("C", bound="ChestModel")


@define()
class ChestModel(Model):
    orbs: int = DEFAULT_ORBS
    diamonds: int = DEFAULT_DIAMONDS
    shard_type: ShardType = ShardType.DEFAULT
    keys: int = DEFAULT_KEYS

    @classmethod
    def from_robtop(cls: Type[C], string: str) -> C:
        orbs, diamonds, shard_type_value, keys = iter(split_chest(string)).map(int).tuple()

        shard_type = ShardType(shard_type_value)

        return cls(orbs=orbs, diamonds=diamonds, shard_type=shard_type, keys=keys)

    def to_robtop(self) -> str:
        return iter.of(
            str(self.orbs), str(self.diamonds), str(self.shard_type.value), str(self.keys)
        ).collect(concat_chest)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return CHEST_SEPARATOR in string


Q = TypeVar("Q", bound="QuestModel")


@define()
class QuestModel(Model):
    id: int = DEFAULT_ID
    type: QuestType = QuestType.DEFAULT
    amount: int = DEFAULT_AMOUNT
    reward: int = DEFAULT_REWARD
    name: str = EMPTY

    @classmethod
    def from_robtop(cls: Type[Q], string: str) -> Q:
        id_string, type_string, amount_string, reward_string, name = split_quest(string)

        id = int(id_string)

        type_value = int(type_string)

        type = QuestType(type_value)

        amount = int(amount_string)

        reward = int(reward_string)

        return cls(id=id, type=type, amount=amount, reward=reward, name=name)

    def to_robtop(self) -> str:
        return iter.of(
            str(self.id), str(self.type.value), str(self.amount), str(self.reward), self.name
        ).collect(concat_quest)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return QUEST_SEPARATOR in string


GAUNTLET_ID = 1
GAUNTLET_LEVEL_IDS = 3


G = TypeVar("G", bound="GauntletModel")


@define()
class GauntletModel(Model):
    id: int = DEFAULT_ID
    level_ids: DynamicTuple[int] = ()

    @classmethod
    def from_robtop(cls: Type[G], string: str) -> G:
        mapping = split_gauntlet(string)

        id = parse_get_or(int, DEFAULT_ID, mapping.get(GAUNTLET_ID))

        level_ids_option = mapping.get(GAUNTLET_LEVEL_IDS)

        level_ids: DynamicTuple[int]

        if level_ids_option is None:
            level_ids = ()

        else:
            level_ids = iter(split_level_ids(level_ids_option)).map(int).tuple()

        return cls(id=id, level_ids=level_ids)

    def to_robtop(self) -> str:
        mapping = {
            GAUNTLET_ID: str(self.id),
            GAUNTLET_LEVEL_IDS: iter(self.level_ids).map(str).collect(concat_level_ids),
        }

        return concat_gauntlet(mapping)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return GAUNTLET_SEPARATOR in string


MAP_PACK_ID = 1
MAP_PACK_NAME = 2
MAP_PACK_LEVEL_IDS = 3
MAP_PACK_STARS = 4
MAP_PACK_COINS = 5
MAP_PACK_DIFFICULTY = 6
MAP_PACK_COLOR = 7
MAP_PACK_OTHER_COLOR = 8

MP = TypeVar("MP", bound="MapPackModel")

DEFAULT_DIFFICULTY_VALUE = Difficulty.DEFAULT.value


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
    def from_robtop(cls: Type[MP], string: str) -> MP:
        mapping = split_map_pack(string)

        id = parse_get_or(int, DEFAULT_ID, mapping.get(MAP_PACK_ID))

        name = mapping.get(MAP_PACK_NAME, EMPTY)

        level_ids_option = mapping.get(MAP_PACK_LEVEL_IDS)

        level_ids: DynamicTuple[int]

        if level_ids_option is None:
            level_ids = ()

        else:
            level_ids = iter(split_level_ids(level_ids_option)).map(int).tuple()

        stars = parse_get_or(int, DEFAULT_STARS, mapping.get(MAP_PACK_STARS))

        coins = parse_get_or(int, DEFAULT_COINS, mapping.get(MAP_PACK_COINS))

        difficulty_value = parse_get_or(
            int, DEFAULT_DIFFICULTY_VALUE, mapping.get(MAP_PACK_DIFFICULTY)
        )

        difficulty = Difficulty(difficulty_value + 1)  # slightly hacky way to convert

        color = parse_get_or_else(Color.from_robtop, Color.default, mapping.get(MAP_PACK_COLOR))

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
            MAP_PACK_DIFFICULTY: str(self.difficulty.value - 1),  # and convert back
            MAP_PACK_COLOR: self.color.to_robtop(),
            MAP_PACK_OTHER_COLOR: self.color.to_robtop(),
        }

        return concat_map_pack(mapping)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return MAP_PACK_SEPARATOR in string


CI = TypeVar("CI", bound="ChestsInnerModel")


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
    def from_robtop(cls: Type[CI], string: str) -> CI:
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

        chest_1_duration_seconds = int(chest_1_duration_string)

        chest_1_duration = duration(seconds=chest_1_duration_seconds)

        chest_1 = ChestModel.from_robtop(chest_1_string)

        chest_1_count = int(chest_1_count_string)

        chest_2_duration_seconds = int(chest_2_duration_string)

        chest_2_duration = duration(seconds=chest_2_duration_seconds)

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
            str(int(self.chest_1_duration.total_seconds())),  # type: ignore
            self.chest_1.to_robtop(),
            str(self.chest_1_count),
            str(int(self.chest_2_duration.total_seconds())),  # type: ignore
            self.chest_2.to_robtop(),
            str(self.chest_2_count),
            str(self.reward_type.value),
        ).collect(concat_chests_inner)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return CHESTS_INNER_SEPARATOR in string


QI = TypeVar("QI", bound="QuestsInnerModel")


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
    def from_robtop(cls: Type[QI], string: str) -> QI:
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

        quest_duration_seconds = int(duration_string)

        quest_duration = duration(seconds=quest_duration_seconds)

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
            str(int(self.quest_duration.total_seconds())),  # type: ignore
            self.quest_1.to_robtop(),
            self.quest_2.to_robtop(),
            self.quest_3.to_robtop(),
        ).collect(concat_quests_inner)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return QUESTS_INNER_SEPARATOR in string


CR = TypeVar("CR", bound="ChestsResponseModel")


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
        return generate_random_string(CHESTS_SLICE) + encode_robtop_string(
            self.inner.to_robtop(), Key.CHESTS
        )

    @staticmethod
    def decode_inner(string: str) -> str:
        return decode_robtop_string(string[CHESTS_SLICE:], Key.CHESTS)

    @classmethod
    def from_robtop(cls: Type[CR], string: str) -> CR:
        string, hash = split_chests_response(string)

        inner_string = cls.decode_inner(string)

        inner = ChestsInnerModel.from_robtop(inner_string)

        return cls(inner=inner, hash=hash)

    def to_robtop(self) -> str:
        return iter.of(self.encode_inner(), self.hash).collect(concat_chests_response)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return CHESTS_RESPONSE_SEPARATOR in string


QR = TypeVar("QR", bound="QuestsResponseModel")


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
        return generate_random_string(QUESTS_SLICE) + encode_robtop_string(
            self.inner.to_robtop(), Key.QUESTS
        )

    @staticmethod
    def decode_inner(string: str) -> str:
        return decode_robtop_string(string[QUESTS_SLICE:], Key.QUESTS)

    @classmethod
    def from_robtop(cls: Type[QR], string: str) -> QR:
        inner_string, hash = split_quests_response(string)

        inner_string = cls.decode_inner(inner_string)

        inner = QuestsInnerModel.from_robtop(inner_string)

        return cls(inner=inner, hash=hash)

    def to_robtop(self) -> str:
        return iter.of(self.encode_inner(), self.hash).collect(concat_quests_response)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return QUESTS_RESPONSE_SEPARATOR in string


def gauntlet_to_robtop(gauntlet: GauntletModel) -> str:
    return gauntlet.to_robtop()


def gauntlet_hash_part(gauntlet: GauntletModel) -> str:
    return iter.of(
        str(gauntlet.id), iter(gauntlet.level_ids).map(str).collect(concat_level_ids)
    ).collect(concat_empty)


GR = TypeVar("GR", bound="GauntletsResponseModel")


@define()
class GauntletsResponseModel(Model):
    gauntlets: List[GauntletModel] = field(factory=list)
    hash: str = field()

    @hash.default
    def default_hash(self) -> str:
        return self.compute_hash()

    def compute_hash(self) -> str:
        return sha1_string_with_salt(
            iter(self.gauntlets).map(gauntlet_hash_part).collect(concat_empty), Salt.LEVEL
        )

    @classmethod
    def from_robtop(cls: Type[GR], string: str) -> GR:
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return GAUNTLETS_RESPONSE_SEPARATOR in string


def map_pack_to_robtop(map_pack: MapPackModel) -> str:
    return map_pack.to_robtop()


def map_packs_hash_part(map_pack: MapPackModel) -> str:
    string = str(map_pack.id)

    return iter.of(first(string), last(string), str(map_pack.stars), str(map_pack.coins)).collect(
        concat_empty
    )


MPR = TypeVar("MPR", bound="MapPacksResponseModel")


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
            iter(self.map_packs).map(map_packs_hash_part).collect(concat_empty), Salt.LEVEL
        )

    @classmethod
    def from_robtop(cls: Type[MPR], string: str) -> MPR:
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return MAP_PACKS_RESPONSE_SEPARATOR in string


def level_leaderboard_user_to_robtop(level_leaderboard_user: LevelLeaderboardUserModel) -> str:
    return level_leaderboard_user.to_robtop()


LLR = TypeVar("LLR", bound="LevelLeaderboardResponseModel")


@define()
class LevelLeaderboardResponseModel(Model):
    users: List[LevelLeaderboardUserModel] = field(factory=list)

    @classmethod
    def from_robtop(cls: Type[LLR], string: str) -> LLR:
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return LEVEL_LEADERBOARD_RESPONSE_USERS_SEPARATOR in string


def level_comment_to_robtop(level_comment: LevelCommentModel) -> str:
    return level_comment.to_robtop()


LCR = TypeVar("LCR", bound="LevelCommentsResponseModel")


@define()
class LevelCommentsResponseModel(Model):
    comments: List[LevelCommentModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[LCR], string: str) -> LCR:
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return LEVEL_COMMENTS_RESPONSE_SEPARATOR in string


def user_comment_to_robtop(user_comment: UserCommentModel) -> str:
    return user_comment.to_robtop()


UCR = TypeVar("UCR", bound="UserCommentsResponseModel")


@define()
class UserCommentsResponseModel(Model):
    comments: List[UserCommentModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[UCR], string: str) -> UCR:
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return USER_COMMENTS_RESPONSE_SEPARATOR in string


SMART_HASH_COUNT = 40


LR = TypeVar("LR", bound="LevelResponseModel")


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

        if creator is None:
            return iter.of(self.level.to_robtop(), self.smart_hash, self.hash).collect(
                concat_level_response
            )

        else:
            return iter.of(
                self.level.to_robtop(), self.smart_hash, self.hash, creator.to_robtop()
            ).collect(concat_level_response)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return LEVEL_RESPONSE_SEPARATOR in string


def search_levels_hash_part(level: LevelModel) -> str:
    string = str(level.id)

    return iter.of(first(string), last(string), str(level.stars), str(level.coins)).collect(
        concat_empty
    )


SLR = TypeVar("SLR", bound="SearchLevelsResponseModel")


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
            iter(self.levels).map(search_levels_hash_part).collect(concat_empty), Salt.LEVEL
        )

    @classmethod
    def from_robtop(cls: Type[SLR], string: str) -> SLR:
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return SEARCH_LEVELS_RESPONSE_SEPARATOR in string


def search_user_to_robtop(search_user: SearchUserModel) -> str:
    return search_user.to_robtop()


SUR = TypeVar("SUR", bound="SearchUsersResponseModel")


@define()
class SearchUsersResponseModel(Model):
    users: List[SearchUserModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[SUR], string: str) -> SUR:
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return SEARCH_USERS_RESPONSE_SEPARATOR in string


def relationship_user_to_robtop(relationship_user: RelationshipUserModel) -> str:
    return relationship_user.to_robtop()


RR = TypeVar("RR", bound="RelationshipsResponseModel")


@define()
class RelationshipsResponseModel(Model):
    users: List[RelationshipUserModel] = field(factory=list)

    @classmethod
    def from_robtop(cls: Type[RR], string: str) -> RR:
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return RELATIONSHIPS_RESPONSE_USERS_SEPARATOR in string


def leaderboard_user_to_robtop(leaderboard_user: LeaderboardUserModel) -> str:
    return leaderboard_user.to_robtop()


LBR = TypeVar("LBR", bound="LeaderboardResponseModel")


@define()
class LeaderboardResponseModel(Model):
    users: List[LeaderboardUserModel] = field(factory=list)

    @classmethod
    def from_robtop(cls: Type[LBR], string: str) -> LBR:
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return LEADERBOARD_RESPONSE_USERS_SEPARATOR in string


def message_to_robtop(message: MessageModel) -> str:
    return message.to_robtop()


MR = TypeVar("MR", bound="MessagesResponseModel")


@define()
class MessagesResponseModel(Model):
    messages: List[MessageModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[MR], string: str) -> MR:
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return MESSAGES_RESPONSE_SEPARATOR in string


def artist_to_robtop(artist: ArtistModel) -> str:
    return artist.to_robtop()


AR = TypeVar("AR", bound="ArtistsResponseModel")


@define()
class ArtistsResponseModel(Model):
    artists: List[ArtistModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[AR], string: str) -> AR:
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return ARTISTS_RESPONSE_SEPARATOR in string


def friend_request_to_robtop(friend_request: FriendRequestModel) -> str:
    return friend_request.to_robtop()


FRR = TypeVar("FRR", bound="FriendRequestsResponseModel")


@define()
class FriendRequestsResponseModel(Model):
    friend_requests: List[FriendRequestModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[FRR], string: str) -> FRR:
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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return MESSAGES_RESPONSE_SEPARATOR in string


TEMPORARY = "temp"


CB = TypeVar("CB", bound="CommentBannedModel")


@define()
class CommentBannedModel(Model):
    string: str = field(default=TEMPORARY)
    timeout: Duration = field(factory=duration)
    reason: str = field(default=EMPTY)

    @classmethod
    def from_robtop(cls: Type[CB], string: str) -> CB:
        string, timeout_string, reason = split_comment_banned(string)

        timeout_seconds = int(timeout_string)

        timeout = duration(seconds=timeout_seconds)

        return cls(string=string, timeout=timeout, reason=reason)

    def to_robtop(self) -> str:
        return iter.of(
            self.string, str(int(self.timeout.total_seconds())), self.reason  # type: ignore
        ).collect(concat_comment_banned)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return COMMENT_BANNED_SEPARATOR in string
