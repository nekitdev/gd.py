from typing import Iterator, List, Optional, Type, TypeVar
from urllib.parse import quote, unquote

from attrs import define, field
from iters import iter
from typing_extensions import Protocol
from yarl import URL

from gd.api.editor import Editor
from gd.color import Color
from gd.constants import (
    CHESTS_SLICE,
    DEFAULT_ACTIVE,
    DEFAULT_AMOUNT,
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
    DEFAULT_EPIC,
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
    TIMELY_ID_ADD,
    UNKNOWN,
    UNNAMED,
)
from gd.date_time import DateTime, Duration, date_time_from_human, date_time_to_human, utc_now
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
from gd.typing import DynamicTuple
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
    def from_robtop(cls: Type[S], string: str) -> S:
        mapping = split_song(string)

        download_url_option = mapping.get(SONG_DOWNLOAD_URL)

        download_url = URL(unquote(download_url_option)) if download_url_option else None

        return cls(
            id=parse_get_or(int, DEFAULT_ID, mapping.get(SONG_ID)),
            name=mapping.get(SONG_NAME, UNKNOWN),
            artist_name=mapping.get(SONG_ARTIST_NAME, UNKNOWN),
            artist_id=parse_get_or(int, DEFAULT_ID, mapping.get(SONG_ARTIST_ID)),
            size=parse_get_or(float, DEFAULT_SIZE, mapping.get(SONG_SIZE)),
            youtube_video_id=mapping.get(SONG_YOUTUBE_VIDEO_ID, EMPTY),
            youtube_channel_id=mapping.get(SONG_YOUTUBE_CHANNEL_ID, EMPTY),
            unknown=mapping.get(SONG_UNKNOWN, EMPTY),
            download_url=download_url,
        )

    def to_robtop(self) -> str:
        mapping = {
            SONG_ID: str(self.id),
            SONG_NAME: self.name,
            SONG_ARTIST_NAME: self.artist_name,
            SONG_ARTIST_ID: str(self.artist_id),
            SONG_SIZE: float_str(self.size),
            SONG_YOUTUBE_VIDEO_ID: self.youtube_video_id,
            SONG_YOUTUBE_CHANNEL_ID: self.youtube_channel_id,
            SONG_UNKNOWN: self.unknown,
            SONG_DOWNLOAD_URL: quote(str(self.download_url or EMPTY)),
        }

        return concat_song(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return SONG_SEPARATOR in string


LG = TypeVar("LG", bound="LoginModel")


@define()
class LoginModel(Model):
    account_id: int = 0
    id: int = 0

    @classmethod
    def from_robtop(cls: Type[LG], string: str) -> LG:
        account_id, id = split_login(string)

        return cls(int(account_id), int(id))

    def to_robtop(self) -> str:
        values = (str(self.account_id), str(self.id))

        return concat_login(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LOGIN_SEPARATOR in string


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

        return cls(total, start, stop)

    def to_robtop(self) -> str:
        total = self.total
        start = self.start
        stop = self.stop

        if total is None:
            values = (EMPTY, str(start), str(stop))

        else:
            values = (str(total), str(start), str(stop))

        return concat_page(values)

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
    def from_robtop(cls: Type[SU], string: str) -> SU:
        mapping = split_search_user(string)

        rank_option = mapping.get(SEARCH_USER_RANK)

        if rank_option:
            rank = int(rank_option)

        else:
            rank = DEFAULT_RANK

        return cls(
            name=mapping.get(SEARCH_USER_NAME, UNKNOWN),
            id=parse_get_or(int, DEFAULT_ID, mapping.get(SEARCH_USER_ID)),
            stars=parse_get_or(int, DEFAULT_STARS, mapping.get(SEARCH_USER_STARS)),
            demons=parse_get_or(int, DEFAULT_DEMONS, mapping.get(SEARCH_USER_DEMONS)),
            rank=rank,
            creator_points=parse_get_or(
                int,
                DEFAULT_CREATOR_POINTS,
                mapping.get(SEARCH_USER_CREATOR_POINTS),
            ),
            icon_id=parse_get_or(int, DEFAULT_ID, mapping.get(SEARCH_USER_ICON_ID)),
            color_1_id=parse_get_or(int, DEFAULT_COLOR_1_ID, mapping.get(SEARCH_USER_COLOR_1_ID)),
            color_2_id=parse_get_or(int, DEFAULT_COLOR_2_ID, mapping.get(SEARCH_USER_COLOR_2_ID)),
            secret_coins=parse_get_or(
                int, DEFAULT_SECRET_COINS, mapping.get(SEARCH_USER_SECRET_COINS)
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                IconType.DEFAULT,
                mapping.get(SEARCH_USER_ICON_TYPE),
            ),
            glow=parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(SEARCH_USER_GLOW)),
            account_id=parse_get_or(int, DEFAULT_ID, mapping.get(SEARCH_USER_ACCOUNT_ID)),
            user_coins=parse_get_or(int, DEFAULT_USER_COINS, mapping.get(SEARCH_USER_USER_COINS)),
        )

    def to_robtop(self) -> str:
        glow = self.glow

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
PROFILE_ROLE_ID = 49
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
    role_id: int = DEFAULT_ID
    comment_state: CommentState = CommentState.DEFAULT

    @classmethod
    def from_robtop(cls: Type[P], string: str) -> P:
        mapping = split_profile(string)

        return cls(
            name=mapping.get(PROFILE_NAME, UNKNOWN),
            id=parse_get_or(int, DEFAULT_ID, mapping.get(PROFILE_ID)),
            stars=parse_get_or(int, DEFAULT_STARS, mapping.get(PROFILE_STARS)),
            demons=parse_get_or(int, DEFAULT_DEMONS, mapping.get(PROFILE_DEMONS)),
            creator_points=parse_get_or(
                int, DEFAULT_CREATOR_POINTS, mapping.get(PROFILE_CREATOR_POINTS)
            ),
            color_1_id=parse_get_or(int, DEFAULT_COLOR_1_ID, mapping.get(PROFILE_COLOR_1_ID)),
            color_2_id=parse_get_or(int, DEFAULT_COLOR_2_ID, mapping.get(PROFILE_COLOR_2_ID)),
            secret_coins=parse_get_or(int, DEFAULT_SECRET_COINS, mapping.get(PROFILE_SECRET_COINS)),
            account_id=parse_get_or(int, DEFAULT_ID, mapping.get(PROFILE_ACCOUNT_ID)),
            user_coins=parse_get_or(int, DEFAULT_USER_COINS, mapping.get(PROFILE_USER_COINS)),
            message_state=parse_get_or(
                partial_parse_enum(int, MessageState),
                MessageState.DEFAULT,
                mapping.get(PROFILE_MESSAGE_STATE),
            ),
            friend_request_state=parse_get_or(
                partial_parse_enum(int, FriendRequestState),
                FriendRequestState.DEFAULT,
                mapping.get(PROFILE_FRIEND_REQUEST_STATE),
            ),
            youtube=mapping.get(PROFILE_YOUTUBE) or None,
            cube_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_CUBE_ID)),
            ship_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_SHIP_ID)),
            ball_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_BALL_ID)),
            ufo_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_UFO_ID)),
            wave_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_WAVE_ID)),
            robot_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_ROBOT_ID)),
            glow=parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(PROFILE_GLOW)),
            active=parse_get_or(int_bool, DEFAULT_ACTIVE, mapping.get(PROFILE_ACTIVE)),
            rank=parse_get_or(int, DEFAULT_RANK, mapping.get(PROFILE_RANK)),
            friend_state=parse_get_or(
                partial_parse_enum(int, FriendState),
                FriendState.DEFAULT,
                mapping.get(PROFILE_FRIEND_STATE),
            ),
            new_messages=parse_get_or(int, DEFAULT_NEW, mapping.get(PROFILE_NEW_MESSAGES)),
            new_friend_requests=parse_get_or(
                int, DEFAULT_NEW, mapping.get(PROFILE_NEW_FRIEND_REQUESTS)
            ),
            new_friends=parse_get_or(int, DEFAULT_NEW, mapping.get(PROFILE_NEW_FRIENDS)),
            spider_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_SPIDER_ID)),
            twitter=mapping.get(PROFILE_TWITTER) or None,
            twitch=mapping.get(PROFILE_TWITCH) or None,
            diamonds=parse_get_or(int, DEFAULT_DIAMONDS, mapping.get(PROFILE_DIAMONDS)),
            explosion_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(PROFILE_EXPLOSION_ID)),
            role_id=parse_get_or(int, DEFAULT_ID, mapping.get(PROFILE_ROLE_ID)),
            comment_state=parse_get_or(
                partial_parse_enum(int, CommentState),
                CommentState.DEFAULT,
                mapping.get(PROFILE_COMMENT_STATE),
            ),
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
            PROFILE_GLOW: str(int(self.glow)),
            PROFILE_ACTIVE: str(int(self.active)),
            PROFILE_RANK: str(int(self.rank)),
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
    def from_robtop(cls: Type[RU], string: str) -> RU:
        mapping = split_relationship_user(string)

        return cls(
            name=mapping.get(RELATIONSHIP_USER_NAME, UNKNOWN),
            id=parse_get_or(int, DEFAULT_ID, mapping.get(RELATIONSHIP_USER_ID)),
            icon_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(RELATIONSHIP_USER_ICON_ID)),
            color_1_id=parse_get_or(
                int, DEFAULT_COLOR_1_ID, mapping.get(RELATIONSHIP_USER_COLOR_1_ID)
            ),
            color_2_id=parse_get_or(
                int, DEFAULT_COLOR_2_ID, mapping.get(RELATIONSHIP_USER_COLOR_2_ID)
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                IconType.DEFAULT,
                mapping.get(RELATIONSHIP_USER_ICON_TYPE),
            ),
            glow=parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(RELATIONSHIP_USER_GLOW)),
            account_id=parse_get_or(int, DEFAULT_ID, mapping.get(RELATIONSHIP_USER_ACCOUNT_ID)),
            message_state=parse_get_or(
                partial_parse_enum(int, MessageState),
                MessageState.DEFAULT,
                mapping.get(RELATIONSHIP_USER_MESSAGE_STATE),
            ),
        )

    def to_robtop(self) -> str:
        glow = self.glow

        glow += glow  # type: ignore

        mapping = {
            RELATIONSHIP_USER_NAME: str(self.name),
            RELATIONSHIP_USER_ID: str(self.id),
            RELATIONSHIP_USER_ICON_ID: str(self.icon_id),
            RELATIONSHIP_USER_COLOR_1_ID: str(self.color_1_id),
            RELATIONSHIP_USER_COLOR_2_ID: str(self.color_2_id),
            RELATIONSHIP_USER_ICON_TYPE: str(self.icon_type.value),
            RELATIONSHIP_USER_GLOW: str(int(glow)),
            RELATIONSHIP_USER_ACCOUNT_ID: str(self.account_id),
            RELATIONSHIP_USER_MESSAGE_STATE: str(self.message_state.value),
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
    def from_robtop(cls: Type[LU], string: str) -> LU:
        mapping = split_leaderboard_user(string)

        return cls(
            name=mapping.get(LEADERBOARD_USER_NAME, UNKNOWN),
            id=parse_get_or(int, DEFAULT_ID, mapping.get(LEADERBOARD_USER_ID)),
            stars=parse_get_or(int, DEFAULT_STARS, mapping.get(LEADERBOARD_USER_STARS)),
            demons=parse_get_or(int, DEFAULT_DEMONS, mapping.get(LEADERBOARD_USER_DEMONS)),
            place=parse_get_or(int, DEFAULT_PLACE, mapping.get(LEADERBOARD_USER_PLACE)),
            creator_points=parse_get_or(
                int, DEFAULT_CREATOR_POINTS, mapping.get(LEADERBOARD_USER_CREATOR_POINTS)
            ),
            icon_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(LEADERBOARD_USER_ICON_ID)),
            color_1_id=parse_get_or(
                int, DEFAULT_COLOR_1_ID, mapping.get(LEADERBOARD_USER_COLOR_1_ID)
            ),
            color_2_id=parse_get_or(
                int, DEFAULT_COLOR_2_ID, mapping.get(LEADERBOARD_USER_COLOR_2_ID)
            ),
            secret_coins=parse_get_or(
                int, DEFAULT_SECRET_COINS, mapping.get(LEADERBOARD_USER_SECRET_COINS)
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                IconType.DEFAULT,
                mapping.get(LEADERBOARD_USER_ICON_TYPE),
            ),
            glow=parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(LEADERBOARD_USER_GLOW)),
            account_id=parse_get_or(int, DEFAULT_ID, mapping.get(LEADERBOARD_USER_ACCOUNT_ID)),
            user_coins=parse_get_or(
                int, DEFAULT_USER_COINS, mapping.get(LEADERBOARD_USER_USER_COINS)
            ),
            diamonds=parse_get_or(int, DEFAULT_DIAMONDS, mapping.get(LEADERBOARD_USER_DIAMONDS)),
        )

    def to_robtop(self) -> str:
        glow = self.glow

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
        cls: Type[M], string: str, content_present: bool = DEFAULT_CONTENT_PRESENT
    ) -> M:
        mapping = split_message(string)

        return cls(
            id=parse_get_or(int, DEFAULT_ID, mapping.get(MESSAGE_ID)),
            account_id=parse_get_or(int, DEFAULT_ID, mapping.get(MESSAGE_ACCOUNT_ID)),
            user_id=parse_get_or(
                int,
                DEFAULT_ID,
                mapping.get(MESSAGE_USER_ID),
            ),
            subject=decode_base64_string_url_safe(mapping.get(MESSAGE_SUBJECT, EMPTY)),
            content=decode_robtop_string(mapping.get(MESSAGE_CONTENT, EMPTY), Key.MESSAGE),
            name=mapping.get(MESSAGE_NAME, UNKNOWN),
            created_at=parse_get_or(
                date_time_from_human, utc_now(), mapping.get(MESSAGE_CREATED_AT), ignore_errors=True
            ),
            read=parse_get_or(int_bool, DEFAULT_READ, mapping.get(MESSAGE_READ)),
            sent=parse_get_or(int_bool, DEFAULT_SENT, mapping.get(MESSAGE_SENT)),
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
            MESSAGE_READ: str(int(self.read)),
            MESSAGE_SENT: str(int(self.sent)),
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
    def from_robtop(cls: Type[FR], string: str) -> FR:
        mapping = split_friend_request(string)

        return cls(
            name=mapping.get(FRIEND_REQUEST_NAME, UNKNOWN),
            user_id=parse_get_or(int, DEFAULT_ID, mapping.get(FRIEND_REQUEST_USER_ID)),
            icon_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(FRIEND_REQUEST_ICON_ID)),
            color_1_id=parse_get_or(
                int, DEFAULT_COLOR_1_ID, mapping.get(FRIEND_REQUEST_COLOR_1_ID)
            ),
            color_2_id=parse_get_or(
                int, DEFAULT_COLOR_2_ID, mapping.get(FRIEND_REQUEST_COLOR_2_ID)
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                IconType.DEFAULT,
                mapping.get(FRIEND_REQUEST_ICON_TYPE),
            ),
            glow=parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(FRIEND_REQUEST_GLOW)),
            account_id=parse_get_or(int, DEFAULT_ID, mapping.get(FRIEND_REQUEST_ACCOUNT_ID)),
            id=parse_get_or(int, DEFAULT_ID, mapping.get(FRIEND_REQUEST_ID)),
            content=decode_base64_string_url_safe(mapping.get(FRIEND_REQUEST_CONTENT, EMPTY)),
            created_at=parse_get_or(
                date_time_from_human,
                utc_now(),
                mapping.get(FRIEND_REQUEST_CREATED_AT),
                ignore_errors=True,
            ),
            unread=parse_get_or(int_bool, DEFAULT_UNREAD, mapping.get(FRIEND_REQUEST_UNREAD)),
        )

    def to_robtop(self) -> str:
        glow = self.glow

        glow += glow  # type: ignore

        unread = self.is_unread()

        unread_string = str(int(unread)) if unread else EMPTY

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
    difficulty: Difficulty = Difficulty.DEFAULT
    downloads: int = DEFAULT_DOWNLOADS
    official_song_id: int = DEFAULT_ID
    game_version: GameVersion = CURRENT_GAME_VERSION
    rating: int = DEFAULT_RATING
    length: LevelLength = LevelLength.DEFAULT
    stars: int = DEFAULT_STARS
    score: int = DEFAULT_SCORE
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
    object_count: int = DEFAULT_OBJECT_COUNT
    editor_time: Duration = field(factory=Duration)
    copies_time: Duration = field(factory=Duration)

    @classmethod
    def from_robtop(cls: Type[L], string: str) -> L:
        mapping = split_level(string)

        difficulty = DifficultyParameters(
            parse_get_or(int, DEFAULT_NUMERATOR, mapping.get(LEVEL_DIFFICULTY_NUMERATOR)),
            parse_get_or(int, DEFAULT_DENOMINATOR, mapping.get(LEVEL_DIFFICULTY_DENOMINATOR)),
            parse_get_or(int, DEFAULT_DEMON_DIFFICULTY_VALUE, mapping.get(LEVEL_DEMON_DIFFICULTY)),
            parse_get_or(int_bool, DEFAULT_AUTO, mapping.get(LEVEL_AUTO)),
            parse_get_or(int_bool, DEFAULT_DEMON, mapping.get(LEVEL_DEMON)),
        ).into_difficulty()

        editor_time_option = mapping.get(LEVEL_EDITOR_TIME)

        if editor_time_option:
            editor_time = Duration(seconds=int(editor_time_option))

        else:
            editor_time = Duration()

        copies_time_option = mapping.get(LEVEL_COPIES_TIME)

        if copies_time_option:
            copies_time = Duration(seconds=int(copies_time_option))

        else:
            copies_time = Duration()

        timely_id = parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_TIMELY_ID))

        if timely_id:
            if timely_id // TIMELY_ID_ADD:
                timely_type = TimelyType.WEEKLY

            else:
                timely_type = TimelyType.DAILY

        else:
            timely_type = TimelyType.NOT_TIMELY

        timely_id %= TIMELY_ID_ADD

        score = parse_get_or(int, DEFAULT_SCORE, mapping.get(LEVEL_SCORE))

        if score < 0:
            score = 0

        return cls(
            id=parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_ID)),
            name=mapping.get(LEVEL_NAME, UNNAMED),
            description=decode_base64_string_url_safe(mapping.get(LEVEL_DESCRIPTION, EMPTY)),
            unprocessed_data=mapping.get(LEVEL_UNPROCESSED_DATA, EMPTY).strip(),
            version=parse_get_or(int, DEFAULT_VERSION, mapping.get(LEVEL_VERSION)),
            creator_id=parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_CREATOR_ID)),
            difficulty=difficulty,
            downloads=parse_get_or(int, DEFAULT_DOWNLOADS, mapping.get(LEVEL_DOWNLOADS)),
            official_song_id=parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_OFFICIAL_SONG_ID)),
            game_version=parse_get_or(
                GameVersion.from_robtop, CURRENT_GAME_VERSION, mapping.get(LEVEL_GAME_VERSION)
            ),
            rating=parse_get_or(int, DEFAULT_RATING, mapping.get(LEVEL_RATING)),
            length=parse_get_or(
                partial_parse_enum(int, LevelLength),
                LevelLength.DEFAULT,
                mapping.get(LEVEL_LENGTH),
            ),
            stars=parse_get_or(int, DEFAULT_STARS, mapping.get(LEVEL_STARS)),
            score=score,
            password_data=parse_get_or(
                Password.from_robtop, Password(), mapping.get(LEVEL_PASSWORD_DATA)
            ),
            created_at=parse_get_or(
                date_time_from_human,
                utc_now(),
                mapping.get(LEVEL_CREATED_AT),
                ignore_errors=True,
            ),
            updated_at=parse_get_or(
                date_time_from_human,
                utc_now(),
                mapping.get(LEVEL_UPDATED_AT),
                ignore_errors=True,
            ),
            original_id=parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_ORIGINAL_ID)),
            two_player=parse_get_or(int_bool, DEFAULT_TWO_PLAYER, mapping.get(LEVEL_TWO_PLAYER)),
            custom_song_id=parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_CUSTOM_SONG_ID)),
            extra_string=mapping.get(LEVEL_EXTRA_STRING, EMPTY),
            coins=parse_get_or(int, DEFAULT_COINS, mapping.get(LEVEL_COINS)),
            verified_coins=parse_get_or(
                int_bool, DEFAULT_VERIFIED_COINS, mapping.get(LEVEL_VERIFIED_COINS)
            ),
            requested_stars=parse_get_or(int, DEFAULT_STARS, mapping.get(LEVEL_REQUESTED_STARS)),
            low_detail=parse_get_or(int_bool, DEFAULT_LOW_DETAIL, mapping.get(LEVEL_LOW_DETAIL)),
            timely_id=timely_id,
            timely_type=timely_type,
            epic=parse_get_or(int_bool, DEFAULT_EPIC, mapping.get(LEVEL_EPIC)),
            object_count=parse_get_or(int, DEFAULT_OBJECT_COUNT, mapping.get(LEVEL_OBJECT_COUNT)),
            editor_time=editor_time,
            copies_time=copies_time,
        )

    def to_robtop(self) -> str:
        timely_id = self.timely_id

        timely_type = self.timely_type

        if timely_type.is_weekly():
            timely_id += TIMELY_ID_ADD

        difficulty_parameters = DifficultyParameters.from_difficulty(self.difficulty)

        demon = difficulty_parameters.is_demon()

        demon_string = str(int(demon)) if demon else EMPTY

        auto = difficulty_parameters.is_auto()

        auto_string = str(int(auto)) if auto else EMPTY

        two_player = self.is_two_player()

        two_player_string = str(int(two_player)) if two_player else EMPTY

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
            LEVEL_EXTRA_STRING: self.extra_string,
            LEVEL_COINS: str(self.coins),
            LEVEL_VERIFIED_COINS: str(int(self.verified_coins)),
            LEVEL_REQUESTED_STARS: str(self.requested_stars),
            LEVEL_LOW_DETAIL: str(int(self.low_detail)),
            LEVEL_TIMELY_ID: str(timely_id),
            LEVEL_EPIC: str(int(self.is_epic())),
            LEVEL_DEMON_DIFFICULTY: str(difficulty_parameters.demon_difficulty_value),
            LEVEL_OBJECT_COUNT: str(self.object_count),
            LEVEL_EDITOR_TIME: str(int(self.editor_time.total_seconds())),
            LEVEL_COPIES_TIME: str(int(self.copies_time.total_seconds())),
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
        return self.epic

    def has_verified_coins(self) -> bool:
        return self.verified_coins

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
        return Editor.from_robtop(self.processed_data).to_bytes()  # type: ignore

    @data.setter
    def data(self, data: bytes) -> None:
        self.processed_data = Editor.from_bytes(data).to_robtop()  # type: ignore


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

        return cls(
            level_id=parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_COMMENT_INNER_LEVEL_ID)),
            content=decode_base64_string_url_safe(mapping.get(LEVEL_COMMENT_INNER_CONTENT, EMPTY)),
            user_id=parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_COMMENT_INNER_USER_ID)),
            rating=parse_get_or(int, DEFAULT_RATING, mapping.get(LEVEL_COMMENT_INNER_RATING)),
            id=parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_COMMENT_INNER_ID)),
            spam=parse_get_or(int_bool, DEFAULT_SPAM, mapping.get(LEVEL_COMMENT_INNER_SPAM)),
            created_at=parse_get_or(
                date_time_from_human,
                utc_now(),
                mapping.get(LEVEL_COMMENT_INNER_CREATED_AT),
                ignore_errors=True,
            ),
            record=parse_get_or(int, DEFAULT_RECORD, mapping.get(LEVEL_COMMENT_INNER_RECORD)),
            role_id=parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_COMMENT_INNER_ROLE_ID)),
            color=parse_get_or(
                Color.from_robtop, Color.default(), mapping.get(LEVEL_COMMENT_INNER_COLOR)
            ),
        )

    def to_robtop(self) -> str:
        mapping = {
            LEVEL_COMMENT_INNER_LEVEL_ID: str(self.level_id),
            LEVEL_COMMENT_INNER_CONTENT: encode_base64_string_url_safe(self.content),
            LEVEL_COMMENT_INNER_USER_ID: str(self.user_id),
            LEVEL_COMMENT_INNER_RATING: str(self.rating),
            LEVEL_COMMENT_INNER_ID: str(self.id),
            LEVEL_COMMENT_INNER_SPAM: str(int(self.spam)),
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
    def from_robtop(cls: Type[LCU], string: str) -> LCU:
        mapping = split_level_comment_user(string)

        return cls(
            name=mapping.get(LEVEL_COMMENT_USER_NAME, UNKNOWN),
            icon_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(LEVEL_COMMENT_USER_ICON_ID)),
            color_1_id=parse_get_or(
                int, DEFAULT_COLOR_1_ID, mapping.get(LEVEL_COMMENT_USER_COLOR_1_ID)
            ),
            color_2_id=parse_get_or(
                int, DEFAULT_COLOR_2_ID, mapping.get(LEVEL_COMMENT_USER_COLOR_2_ID)
            ),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                IconType.DEFAULT,
                mapping.get(LEVEL_COMMENT_USER_ICON_TYPE),
            ),
            glow=parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(LEVEL_COMMENT_USER_GLOW)),
            account_id=parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_COMMENT_USER_ACCOUNT_ID)),
        )

    def to_robtop(self) -> str:
        glow = self.glow

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

        return cls(
            content=decode_base64_string_url_safe(mapping.get(USER_COMMENT_CONTENT, EMPTY)),
            rating=parse_get_or(int, DEFAULT_RATING, mapping.get(USER_COMMENT_RATING)),
            id=parse_get_or(int, DEFAULT_ID, mapping.get(USER_COMMENT_ID)),
            created_at=parse_get_or(
                date_time_from_human,
                utc_now(),
                mapping.get(USER_COMMENT_CREATED_AT),
                ignore_errors=True,
            ),
        )

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
    def from_robtop(cls: Type[LLU], string: str) -> LLU:
        mapping = split_level_leaderboard_user(string)

        return cls(
            name=mapping.get(LEVEL_LEADERBOARD_USER_NAME, UNKNOWN),
            id=parse_get_or(int, DEFAULT_ID, mapping.get(LEVEL_LEADERBOARD_USER_ID)),
            record=parse_get_or(int, DEFAULT_RECORD, mapping.get(LEVEL_LEADERBOARD_USER_RECORD)),
            place=parse_get_or(int, DEFAULT_PLACE, mapping.get(LEVEL_LEADERBOARD_USER_PLACE)),
            icon_id=parse_get_or(int, DEFAULT_ICON_ID, mapping.get(LEVEL_LEADERBOARD_USER_ICON_ID)),
            color_1_id=parse_get_or(
                int, DEFAULT_COLOR_1_ID, mapping.get(LEVEL_LEADERBOARD_USER_COLOR_1_ID)
            ),
            color_2_id=parse_get_or(
                int, DEFAULT_COLOR_2_ID, mapping.get(LEVEL_LEADERBOARD_USER_COLOR_2_ID)
            ),
            coins=parse_get_or(int, DEFAULT_COINS, mapping.get(LEVEL_LEADERBOARD_USER_COINS)),
            icon_type=parse_get_or(
                partial_parse_enum(int, IconType),
                IconType.DEFAULT,
                mapping.get(LEVEL_LEADERBOARD_USER_ICON_TYPE),
            ),
            glow=parse_get_or(int_bool, DEFAULT_GLOW, mapping.get(LEVEL_LEADERBOARD_USER_GLOW)),
            recorded_at=parse_get_or(
                date_time_from_human,
                utc_now(),
                mapping.get(LEVEL_LEADERBOARD_USER_RECORDED_AT),
                ignore_errors=True,
            ),
        )

    def to_robtop(self) -> str:
        glow = self.glow

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

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_LEADERBOARD_USER_SEPARATOR in string


ARTIST_NAME = 4


A = TypeVar("A", bound="ArtistModel")


@define()
class ArtistModel(Model):
    name: str = UNKNOWN

    @classmethod
    def from_robtop(cls: Type[A], string: str) -> A:
        mapping = split_artist(string)

        return cls(name=mapping.get(ARTIST_NAME, UNKNOWN))

    def to_robtop(self) -> str:
        mapping = {ARTIST_NAME: self.name}

        return concat_artist(mapping)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
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
        orbs_string, diamonds_string, shard_type_string, keys_string = split_chest(string)

        return cls(
            orbs=int(orbs_string),
            diamonds=int(diamonds_string),
            shard_type=ShardType(int(shard_type_string)),
            keys=int(keys_string),
        )

    def to_robtop(self) -> str:
        values = (str(self.orbs), str(self.diamonds), str(self.shard_type.value), str(self.keys))

        return concat_chest(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return CHEST_SEPARATOR in string


Q = TypeVar("Q", bound="QuestModel")


@define()
class QuestModel(Model):
    id: int = DEFAULT_ID
    type: QuestType = QuestType.DEFAULT
    amount: int = DEFAULT_AMOUNT
    reward: int = DEFAULT_REWARD
    name: str = UNKNOWN

    @classmethod
    def from_robtop(cls: Type[Q], string: str) -> Q:
        id_string, type_string, amount_string, reward_string, name = split_quest(string)

        return cls(
            id=int(id_string),
            type=QuestType(int(type_string)),
            amount=int(amount_string),
            reward=int(reward_string),
            name=name,
        )

    def to_robtop(self) -> str:
        values = (str(self.id), str(self.type.value), str(self.amount), str(self.reward), self.name)

        return concat_quest(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
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

        level_ids_option = mapping.get(GAUNTLET_LEVEL_IDS)

        level_ids: DynamicTuple[int]

        if level_ids_option is None:
            level_ids = ()

        else:
            level_ids = iter(split_level_ids(level_ids_option)).map(int).tuple()

        return cls(
            id=parse_get_or(int, DEFAULT_ID, mapping.get(GAUNTLET_ID)),
            level_ids=level_ids,
        )

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

MP = TypeVar("MP", bound="MapPackModel")

DEFAULT_DIFFICULTY_VALUE = Difficulty.DEFAULT.value


@define()
class MapPackModel(Model):
    id: int = field(default=DEFAULT_ID)
    name: str = field(default=UNKNOWN)
    level_ids: DynamicTuple[int] = field(default=())
    stars: int = field(default=DEFAULT_STARS)
    coins: int = field(default=DEFAULT_COINS)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT)
    color: Color = field(factory=Color.default)

    @classmethod
    def from_robtop(cls: Type[MP], string: str) -> MP:
        mapping = split_map_pack(string)

        difficulty_value = parse_get_or(
            int, DEFAULT_DIFFICULTY_VALUE, mapping.get(MAP_PACK_DIFFICULTY)
        )

        difficulty = Difficulty(difficulty_value + 1)  # slightly hacky way to convert

        level_ids_option = mapping.get(MAP_PACK_LEVEL_IDS)

        level_ids: DynamicTuple[int]

        if level_ids_option is None:
            level_ids = ()

        else:
            level_ids = iter(split_level_ids(level_ids_option)).map(int).tuple()

        return cls(
            id=parse_get_or(int, DEFAULT_ID, mapping.get(MAP_PACK_ID)),
            name=mapping.get(MAP_PACK_NAME, UNKNOWN),
            level_ids=level_ids,
            stars=parse_get_or(int, DEFAULT_STARS, mapping.get(MAP_PACK_STARS)),
            coins=parse_get_or(int, DEFAULT_COINS, mapping.get(MAP_PACK_COINS)),
            difficulty=difficulty,
            color=parse_get_or(Color.from_robtop, Color.default(), mapping.get(MAP_PACK_COLOR)),
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

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return MAP_PACK_SEPARATOR in string


CI = TypeVar("CI", bound="ChestsInnerModel")


@define()
class ChestsInnerModel(Model):
    random_string: str = field(default=EMPTY)
    user_id: int = field(default=DEFAULT_ID)
    check: str = field(default=EMPTY)
    udid: str = field(default=EMPTY)
    account_id: int = field(default=DEFAULT_ID)
    chest_1_duration: Duration = field(factory=Duration)
    chest_1: ChestModel = field(factory=ChestModel)
    chest_1_count: int = field(default=DEFAULT_CHEST_COUNT)
    chest_2_duration: Duration = field(factory=Duration)
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

        return cls(
            random_string=random_string,
            user_id=int(user_id_string),
            check=check,
            udid=udid,
            account_id=int(account_id_string),
            chest_1_duration=Duration(seconds=int(chest_1_duration_string)),
            chest_1=ChestModel.from_robtop(chest_1_string),
            chest_1_count=int(chest_1_count_string),
            chest_2_duration=Duration(seconds=int(chest_2_duration_string)),
            chest_2=ChestModel.from_robtop(chest_2_string),
            chest_2_count=int(chest_2_count_string),
            reward_type=RewardType(int(reward_type_string)),
        )

    def to_robtop(self) -> str:
        values = (
            self.random_string,
            str(self.user_id),
            self.check,
            self.udid,
            str(self.account_id),
            str(int(self.chest_1_duration.total_seconds())),
            self.chest_1.to_robtop(),
            str(self.chest_1_count),
            str(int(self.chest_2_duration.total_seconds())),
            self.chest_2.to_robtop(),
            str(self.chest_2_count),
            str(self.reward_type.value),
        )

        return concat_chests_inner(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return CHESTS_INNER_SEPARATOR in string


QI = TypeVar("QI", bound="QuestsInnerModel")


@define()
class QuestsInnerModel(Model):
    random_string: str = field(default=EMPTY)
    user_id: int = field(default=DEFAULT_ID)
    check: str = field(default=EMPTY)
    udid: str = field(default=EMPTY)
    account_id: int = field(default=DEFAULT_ID)
    duration: Duration = field(factory=Duration)
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

        return cls(
            random_string=random_string,
            user_id=int(user_id_string),
            check=check,
            udid=udid,
            account_id=int(account_id_string),
            duration=Duration(seconds=int(duration_string)),
            quest_1=QuestModel.from_robtop(quest_1_string),
            quest_2=QuestModel.from_robtop(quest_2_string),
            quest_3=QuestModel.from_robtop(quest_3_string),
        )

    def to_robtop(self) -> str:
        values = (
            self.random_string,
            str(self.user_id),
            self.check,
            self.udid,
            str(self.account_id),
            str(int(self.duration.total_seconds())),
            self.quest_1.to_robtop(),
            self.quest_2.to_robtop(),
            self.quest_3.to_robtop(),
        )

        return concat_quests_inner(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return QUESTS_INNER_SEPARATOR in string


CR = TypeVar("CR", bound="ChestsResponseModel")


@define()
class ChestsResponseModel(Model):
    inner: ChestsInnerModel = field(factory=ChestsInnerModel)
    hash: str = field()

    @hash.default
    def default_hash(self) -> str:
        return sha1_string_with_salt(self.encode_inner(), Salt.CHESTS)

    def encode_inner(self) -> str:
        return generate_random_string(CHESTS_SLICE) + encode_robtop_string(
            self.inner.to_robtop(), Key.CHESTS
        )

    @classmethod
    def decode_inner(cls, string: str) -> str:
        return decode_robtop_string(string[CHESTS_SLICE:], Key.CHESTS)

    @classmethod
    def from_robtop(cls: Type[CR], string: str) -> CR:
        inner_string, hash = split_chests_response(string)

        inner_string = cls.decode_inner(inner_string)

        return cls(inner=ChestsInnerModel.from_robtop(inner_string), hash=hash)

    def to_robtop(self) -> str:
        values = (self.encode_inner(), self.hash)

        return concat_chests_response(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return CHESTS_RESPONSE_SEPARATOR in string


QR = TypeVar("QR", bound="QuestsResponseModel")


@define()
class QuestsResponseModel(Model):
    inner: QuestsInnerModel = field(factory=QuestsInnerModel)
    hash: str = field()

    @hash.default
    def default_hash(self) -> str:
        return sha1_string_with_salt(self.encode_inner(), Salt.QUESTS)

    def encode_inner(self) -> str:
        return generate_random_string(QUESTS_SLICE) + encode_robtop_string(
            self.inner.to_robtop(), Key.QUESTS
        )

    @classmethod
    def decode_inner(cls, string: str) -> str:
        return decode_robtop_string(string[QUESTS_SLICE:], Key.QUESTS)

    @classmethod
    def from_robtop(cls: Type[QR], string: str) -> QR:
        inner_string, hash = split_quests_response(string)

        inner_string = cls.decode_inner(inner_string)

        return cls(inner=QuestsInnerModel.from_robtop(inner_string), hash=hash)

    def to_robtop(self) -> str:
        values = (self.encode_inner(), self.hash)

        return concat_quests_response(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return QUESTS_RESPONSE_SEPARATOR in string


GR = TypeVar("GR", bound="GauntletsResponseModel")


@define()
class GauntletsResponseModel(Model):
    gauntlets: List[GauntletModel] = field(factory=list)
    hash: str = field()

    def default_hash_iterator(self) -> Iterator[str]:
        for gauntlet in self.gauntlets:
            values = (str(gauntlet.id), concat_level_ids(map(str, gauntlet.level_ids)))

            yield concat_empty(values)

    @hash.default
    def default_hash(self) -> str:
        return sha1_string_with_salt(concat_empty(self.default_hash_iterator()), Salt.LEVEL)

    @classmethod
    def from_robtop(cls: Type[GR], string: str) -> GR:
        gauntlets_string, hash = split_gauntlets_response(string)

        gauntlets = [
            GauntletModel.from_robtop(gauntlets_string)
            for gauntlets_string in split_gauntlets_response_gauntlets(gauntlets_string)
        ]

        return cls(gauntlets=gauntlets, hash=hash)

    def to_robtop(self) -> str:
        values = (
            concat_gauntlets_response_gauntlets(
                gauntlet.to_robtop() for gauntlet in self.gauntlets
            ),
            self.hash,
        )

        return concat_gauntlets_response(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return GAUNTLETS_RESPONSE_SEPARATOR in string


MPR = TypeVar("MPR", bound="MapPacksResponseModel")


@define()
class MapPacksResponseModel(Model):
    map_packs: List[MapPackModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)
    hash: str = field()

    def default_hash_iterator(self) -> Iterator[str]:
        first = FIRST
        last = LAST

        for map_pack in self.map_packs:
            string = str(map_pack.id)

            values = (string[first], string[last], str(map_pack.stars), str(map_pack.coins))

            yield concat_empty(values)

    @hash.default
    def default_hash(self) -> str:
        return sha1_string_with_salt(concat_empty(self.default_hash_iterator()), Salt.LEVEL)

    @classmethod
    def from_robtop(cls: Type[MPR], string: str) -> MPR:
        map_packs_string, page_string, hash = split_map_packs_response(string)

        map_packs = [
            MapPackModel.from_robtop(map_pack_string)
            for map_pack_string in split_map_packs_response_map_packs(map_packs_string)
        ]

        page = PageModel.from_robtop(page_string)

        return cls(map_packs=map_packs, page=page, hash=hash)

    def to_robtop(self) -> str:
        values = (
            concat_map_packs_response_map_packs(
                map_pack.to_robtop() for map_pack in self.map_packs
            ),
            self.page.to_robtop(),
            self.hash,
        )

        return concat_map_packs_response(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return MAP_PACKS_RESPONSE_SEPARATOR in string


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


FIRST = 0
LAST = ~0


SLR = TypeVar("SLR", bound="SearchLevelsResponseModel")


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


AR = TypeVar("AR", bound="ArtistsResponseModel")


@define()
class ArtistsResponseModel(Model):
    artists: List[ArtistModel] = field(factory=list)
    page: PageModel = field(factory=PageModel)

    @classmethod
    def from_robtop(cls: Type[AR], string: str) -> AR:
        artists_string, page_string = split_artists_response(string)

        artists = [
            ArtistModel.from_robtop(string)
            for string in split_artists_response_artists(artists_string)
        ]

        page = PageModel.from_robtop(page_string)

        return cls(artists=artists, page=page)

    def to_robtop(self) -> str:
        values = (
            concat_artists_response_artists(artist.to_robtop() for artist in self.artists),
            self.page.to_robtop(),
        )

        return concat_artists_response(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return ARTISTS_RESPONSE_SEPARATOR in string


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


CB = TypeVar("CB", bound="CommentBannedModel")


@define()
class CommentBannedModel(Model):
    string: str = field(default=TEMPORARY)
    timeout: Duration = field(factory=Duration)
    reason: str = field(default=EMPTY)

    @classmethod
    def from_robtop(cls: Type[CB], string: str) -> CB:
        string, timeout, reason = split_comment_banned(string)

        return cls(string, Duration(seconds=int(timeout)), reason)

    def to_robtop(self) -> str:
        values = (self.string, str(int(self.timeout.total_seconds())), self.reason)

        return concat_comment_banned(values)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return COMMENT_BANNED_SEPARATOR in string
