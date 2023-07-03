from __future__ import annotations

from asyncio import Lock, get_running_loop, new_event_loop, set_event_loop, sleep
from atexit import register as register_at_exit
from builtins import getattr as get_attribute
from builtins import setattr as set_attribute
from io import BytesIO
from pathlib import Path
from random import randrange as get_random_range
from types import TracebackType as Traceback
from typing import (
    Any,
    BinaryIO,
    ClassVar,
    Generic,
    Mapping,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    overload,
)
from uuid import uuid4 as generate_uuid

from aiohttp import BasicAuth, ClientError, ClientSession, ClientTimeout
from attrs import define, evolve, field, frozen
from iters.iters import iter
from iters.utils import unary_tuple
from pendulum import Duration, duration
from tqdm import tqdm as progress
from typing_aliases import (
    AnyError,
    DynamicTuple,
    Headers,
    IntoParameters,
    IntoPath,
    Namespace,
    NormalError,
    Parameters,
)
from typing_aliases import Payload as JSON
from typing_aliases import is_bytes, is_string
from typing_extensions import Literal
from yarl import URL

from gd.api.recording import Recording
from gd.asyncio import run_blocking, shutdown_loop
from gd.capacity import Capacity
from gd.constants import (
    DEFAULT_ATTEMPTS,
    DEFAULT_CHECK,
    DEFAULT_CHEST_COUNT,
    DEFAULT_CLICKS,
    DEFAULT_COINS,
    DEFAULT_COUNT,
    DEFAULT_ID,
    DEFAULT_LOW_DETAIL,
    DEFAULT_OBJECT_COUNT,
    DEFAULT_PAGE,
    DEFAULT_RECORD,
    DEFAULT_SECONDS,
    DEFAULT_SEND,
    DEFAULT_SPECIAL,
    DEFAULT_STARS,
    DEFAULT_TWO_PLAYER,
    DEFAULT_VERSION,
    EMPTY,
    SLASH,
    UNNAMED,
    WEEKLY_ID_ADD,
    WRITE_BINARY,
)
from gd.encoding import (
    ATTEMPTS_ADD,
    CLICKS_ADD,
    COINS_ADD,
    SECONDS_ADD,
    UTF_8,
    encode_base64_string_url_safe,
    encode_robtop_string,
    generate_check,
    generate_leaderboard_seed,
    generate_level_seed,
    generate_random_string,
    generate_random_string_and_encode_value,
    zip_level_string,
)
from gd.enums import (
    AccountURLType,
    CommentState,
    CommentStrategy,
    CommentType,
    DemonDifficulty,
    FriendRequestState,
    FriendRequestType,
    IconType,
    Key,
    LeaderboardStrategy,
    LevelLeaderboardStrategy,
    LevelLength,
    LevelPrivacy,
    LikeType,
    MessageState,
    MessageType,
    RelationshipType,
    ResponseType,
    RewardType,
    Salt,
    Secret,
    TimelyType,
)
from gd.errors import (
    CommentBanned,
    HTTPErrorWithOrigin,
    HTTPStatusError,
    LoginFailed,
    LoginRequired,
    MissingAccess,
    NothingFound,
    SongRestricted,
)
from gd.filters import Filters
from gd.models import CommentBannedModel
from gd.models_constants import OBJECT_SEPARATOR
from gd.models_utils import bool_str
from gd.password import Password
from gd.progress import Progress
from gd.string_utils import concat_comma, password_str, snake_to_camel_with_abbreviations, tick
from gd.timer import now
from gd.typing import AnyString, IntString, MaybeIterable, URLString, is_iterable
from gd.version import python_version_info, version_info
from gd.versions import CURRENT_BINARY_VERSION, CURRENT_GAME_VERSION, GameVersion, RobTopVersion

__all__ = ("Route", "HTTPClient")

DATABASE = "database"

BASE = "http://www.boomlings.com/database"
GD_BASE = "http://geometrydash.com/database"

NEWGROUNDS_SONG = "https://newgrounds.com/audio/listen/{}"
NEWGROUNDS_SONG_PAGE = "https://{}.newgrounds.com/audio/page/{}"
NEWGROUNDS_SEARCH = "https://newgrounds.com/search/conduct/{}"

ACCEPT_ENCODING = "Accept-Encoding"
USER_AGENT = "User-Agent"

FORWARDED_FOR = "X-Forwarded-For"
REQUESTED_WITH = "X-Requested-With"

# I might sound stupid but I really like `XMLHTTPRequest` more, and so I wrote this ~ nekit
XML = "XML"
HTTP = "HTTP"
REQUEST = "Request"
XML_HTTP_REQUEST = XML + HTTP.title() + REQUEST

LOGIN = "accounts/loginGJAccount.php"
LOAD = "accounts/syncGJAccountNew.php"
SAVE = "accounts/backupGJAccountNew.php"
GET_ACCOUNT_URL = "getAccountURL.php"
GET_ROLE_ID = "requestUserAccess.php"
UPDATE_SETTINGS = "updateGJAccSettings20.php"
UPDATE_PROFILE = "updateGJUserScore22.php"
GET_USERS = "getGJUsers20.php"
GET_USER = "getGJUserInfo20.php"
GET_RELATIONSHIPS = "getGJUserList20.php"
GET_LEADERBOARD = "getGJScores20.php"
GET_LEVELS = "getGJLevels21.php"
GET_TIMELY = "getGJDailyLevel.php"
GET_LEVEL = "downloadGJLevel22.php"
REPORT_LEVEL = "reportGJLevel.php"
DELETE_LEVEL = "deleteGJLevelUser20.php"
UPDATE_LEVEL_DESCRIPTION = "updateGJDesc20.php"
UPLOAD_LEVEL = "uploadGJLevel21.php"
RATE_LEVEL = "rateGJStars211.php"
RATE_DEMON = "rateGJDemon21.php"
SUGGEST_LEVEL = "suggestGJStars20.php"
GET_LEVEL_LEADERBOARD = "getGJLevelScores211.php"
UNBLOCK_USER = "unblockGJUser20.php"
BLOCK_USER = "blockGJUser20.php"
UNFRIEND_USER = "removeGJFriend20.php"
SEND_MESSAGE = "uploadGJMessage20.php"
GET_MESSAGE = "downloadGJMessage20.php"
DELETE_MESSAGE = "deleteGJMessages20.php"
GET_MESSAGES = "getGJMessages20.php"
SEND_FRIEND_REQUEST = "uploadFriendRequest20.php"
DELETE_FRIEND_REQUEST = "deleteGJFriendRequests20.php"
ACCEPT_FRIEND_REQUEST = "acceptGJFriendRequest20.php"
READ_FRIEND_REQUEST = "readGJFriendRequest20.php"
GET_FRIEND_REQUESTS = "getGJFriendRequests20.php"
LIKE_LEVEL = "likeGJItem211.php"
LIKE_USER_COMMENT = "likeGJItem211.php"
LIKE_LEVEL_COMMENT = "likeGJItem211.php"
POST_LEVEL_COMMENT = "uploadGJComment21.php"
POST_USER_COMMENT = "uploadGJAccComment20.php"
DELETE_LEVEL_COMMENT = "deleteGJComment20.php"
DELETE_USER_COMMENT = "deleteGJAccComment20.php"
GET_USER_LEVEL_COMMENTS = "getGJCommentHistory.php"
GET_USER_COMMENTS = "getGJAccountComments20.php"
GET_LEVEL_COMMENTS = "getGJComments21.php"
GET_GAUNTLETS = "getGJGauntlets21.php"
GET_MAP_PACKS = "getGJMapPacks21.php"
GET_QUESTS = "getGJChallenges.php"
GET_CHESTS = "getGJRewards.php"
GET_ARTISTS = "getGJTopArtists.php"
GET_SONG = "getGJSongInfo.php"

VALID_ERRORS = (OSError, ClientError)

HEAD = "HEAD"
GET = "GET"

POST = "POST"
PUT = "PUT"
PATCH = "PATCH"

DELETE = "DELETE"

CONNECT = "CONNECT"
OPTIONS = "OPTIONS"
TRACE = "TRACE"

HTTP_SUCCESS = 200
HTTP_REDIRECT = 300
HTTP_ERROR = 400

CHUNK_SIZE = 65536

NO_TOTAL = 0

ResponseData = Union[bytes, str, JSON]


UNEXPECTED_ERROR_CODE = "got an unexpected error code: {}"


def unexpected_error_code(error_code: int) -> MissingAccess:
    return MissingAccess(UNEXPECTED_ERROR_CODE.format(tick(error_code)))


DEFAULT_TO_CAMEL = False


P = TypeVar("P", bound="Payload")


class Payload(Namespace):
    def __init__(
        self,
        into_parameters: IntoParameters = (),
        *,
        to_camel: bool = DEFAULT_TO_CAMEL,
        **parameters: Any,
    ) -> None:
        payload = dict(into_parameters)

        payload.update(parameters)

        if to_camel:
            payload = {
                snake_to_camel_with_abbreviations(name): value for name, value in payload.items()
            }

        super().__init__(payload)

    def update(  # type: ignore
        self,
        into_parameters: IntoParameters = (),
        *,
        to_camel: bool = DEFAULT_TO_CAMEL,
        **parameters: Any,
    ) -> None:
        payload = dict(into_parameters)

        payload.update(parameters)

        if to_camel:
            payload = {
                snake_to_camel_with_abbreviations(name): value for name, value in payload.items()
            }

        super().update(payload)

    def copy(self: P) -> P:
        return type(self)(self)


ROUTE = "{} {}"

R = TypeVar("R", bound="Route")


@frozen()
class Route:
    method: str = field()
    route: str = field()
    parameters: Parameters = field(factory=dict)

    @property
    def actual_route(self) -> str:
        return self.route.format_map(self.parameters)

    def __str__(self) -> str:
        return ROUTE.format(self.method, tick(self.actual_route))

    def with_parameters(self: R, parameters: Parameters) -> R:
        return evolve(self, parameters=parameters)


CLIENTS: Set[HTTPClient] = set()


def add_client(client: HTTPClient) -> None:
    CLIENTS.add(client)


def remove_client(client: HTTPClient) -> None:
    CLIENTS.remove(client)


async def close_all_clients() -> None:
    for client in CLIENTS:
        await client.close()

    CLIENTS.clear()


def close_all_clients_sync() -> None:
    loop = new_event_loop()

    set_event_loop(loop)

    loop.run_until_complete(close_all_clients())

    shutdown_loop(loop)


register_at_exit(close_all_clients_sync)


def try_parse_error_code(string: AnyString) -> Optional[int]:
    try:
        error_code = int(string)

    except ValueError:
        return None

    else:
        if error_code < 0:
            return error_code

        return None


def int_or(string: str, default: int) -> int:
    try:
        return int(string)

    except ValueError:
        return default


DEFAULT_USER_AGENT = "python/{} gd.py/{}"

DEFAULT_TIMEOUT = 150.0

DEFAULT_GD_WORLD = False

DEFAULT_SEND_USER_AGENT = False

DEFAULT_WITH_BAR = False

DEFUALT_RETRIES = 2

DEFAULT_READ = True

UDID_PREFIX = "S"
UDID_START = 100_000
UDID_STOP = 100_000_000

VALUE_START = 100
VALUE_STOP = 100000

LOOP = "_loop"  # NOTE: keep in sync with the upstream library

UNIT = "b"
UNIT_SCALE = True

ErrorCodes = Mapping[int, AnyError]

C = TypeVar("C", bound="HTTPClient")

NAME_TOO_SHORT = "`name` is too short"
PASSWORD_TOO_SHORT = "`password` is too short"
LINKED_TO_DIFFERENT = "already linked to a different account"
INCORRECT_CREDENTIALS = "incorrect credentials: {}, password {}"
ACCOUNT_DISABLED = "account {} is disabled"
LINKED_TO_DIFFERENT_STEAM = "already linked to a different steam account"

DATA_TOO_LARGE = "data is too large"
SOMETHING_WENT_WRONG = "something went wrong on the servers' side"

FAILED_TO_FIND_URL = "failed to find {} URL for user with ID {}"

NO_ROLE_FOUND = "no role found"

FAILED_TO_UPDATE_SETTINGS = "failed to update settings"
FAILED_TO_UPDATE_PROFILE = "failed to update profile (ID: {})"

CAN_NOT_FIND_USERS = "can not find users by query {}"

CAN_NOT_FIND_USER = "can not find user with ID: {}"
CAN_NOT_FIND_TYPE_USERS = "can not find {} users"

FAILED_TO_FIND_LEADERBOARD = "failed to find {} leaderboard"

STRATEGY_LEADERBOARD_REQUIRES_LOGIN = "{} strategy requires logged in client"

BY_USER_STRATEGY_REQUIRES_LOGIN = "`by_user` strategy requires logged in client"
FRIENDS_STRATEGY_REQUIRES_LOGIN = "`friends` strategy requires logged in client"

CAN_NOT_GET_LEVEL = "can not get level with ID: {}"

FAILED_TO_REPORT_LEVEL = "failed to report level with ID: {}"
FAILED_TO_DELETE_LEVEL = "failed to delete level with ID: {}"

CAN_NOT_UPDATE_LEVEL_DESCRIPTION = "can not update level description (ID: {})"

EXPECTED_TIMELY = "expected timely type"
CAN_NOT_FIND_TIMELY = "can not find {} level"

FAILED_TO_UPLOAD_LEVEL = "failed to upload a level"

FAILED_TO_RATE_LEVEL = "failed to rate the level (ID: {})"

FAILED_TO_RATE_DEMON = "failed to demon-rate the level (ID: {})"
RATE_DEMON_MISSING_PERMISSIONS = "missing permissions to demon-rate the level (ID: {})"

FAILED_TO_SUGGEST_LEVEL = "failed to suggest the level (ID: {})"
SUGGEST_LEVEL_MISSING_PERMISSIONS = "missing permissions to suggest the level (ID: {})"

FAILED_TO_GET_LEADERBOARD = "failed to get the level leaderboard (ID: {})"

FAILED_TO_BLOCK_USER = "failed to block the user (ID: {})"
FAILED_TO_UNBLOCK_USER = "failed to unblock the user (ID: {})"

FAILED_TO_UNFRIEND_USER = "failed to unfriend the user (ID: {})"

FAILED_TO_SEND_MESSAGE = "failed to send a message to the user (ID: {})"

FAILED_TO_GET_MESSAGE = "failed to get the message (ID: {})"

FAILED_TO_DELETE_MESSAGE = "failed to delete the message (ID: {})"

FAILED_TO_GET_MESSAGES = "failed to get messages on page {}"

FAILED_TO_SEND_FRIEND_REQUEST = "failed to send the friend request (ID: {})"

FAILED_TO_DELETE_FRIEND_REQUEST = "failed to delete the friend request (ID: {})"

FAILED_TO_ACCEPT_FRIEND_REQUEST = "failed to accept the friend request (ID: {})"

FAILED_TO_READ_FRIEND_REQUEST = "failed to read the friend request (ID: {})"

FAILED_TO_GET_FRIEND_REQUESTS = "failed to get friend requests on page {}"

FAILED_TO_LIKE_LEVEL = "failed to like the level (ID: {})"
FAILED_TO_LIKE_USER_COMMENT = "failed to like the user comment (ID: {})"
FAILED_TO_LIKE_LEVEL_COMMENT = "failed to like the level comment (ID: {})"

FAILED_TO_POST_USER_COMMENT = "failed to post the user comment"

FAILED_TO_POST_LEVEL_COMMENT = "failed to post the level comment"

FAILED_TO_DELETE_USER_COMMENT = "failed to delete the user comment (ID: {})"

FAILED_TO_DELETE_LEVEL_COMMENT = "failed to delete the level comment (ID: {})"

FAILED_TO_GET_USER_COMMENTS = "failed to get user comments (ID: {})"

FAILED_TO_GET_USER_LEVEL_COMMENTS = "failed to get user level comments (ID: {})"

FAILED_TO_GET_LEVEL_COMMENTS = "failed to get level comments (ID: {})"

FAILED_TO_GET_GAUNTLETS = "failed to get gauntlets"

FAILED_TO_GET_MAP_PACKS = "failed to get map packs on page {}"

FAILED_TO_GET_QUESTS = "failed to get quests"

FAILED_TO_GET_CHESTS = "failed to get chests"

FAILED_TO_GET_ARTISTS = "failed to get artists"

FAILED_TO_GET_SONG = "failed to get the song (ID: {})"

AUDIO = "audio"
USERS = "users"
LEVELS = "levels"
MESSAGES = "messages"
FRIEND_REQUESTS = "friend_requests"
LEVEL_COMMENTS = "level_comments"


@define()
class HTTPClient:
    SKIP_HEADERS: ClassVar[DynamicTuple[str]] = (ACCEPT_ENCODING, USER_AGENT)

    USER_AGENT: ClassVar[str] = DEFAULT_USER_AGENT.format(python_version_info, version_info)

    url: URLString = field(default=BASE)
    proxy: Optional[str] = field(default=None, repr=False)
    proxy_auth: Optional[BasicAuth] = field(default=None, repr=False)
    timeout: float = field(default=DEFAULT_TIMEOUT)
    game_version: GameVersion = field(default=CURRENT_GAME_VERSION)
    binary_version: RobTopVersion = field(default=CURRENT_BINARY_VERSION)
    gd_world: bool = field(default=DEFAULT_GD_WORLD)
    forwarded_for: Optional[str] = field(default=None, repr=False)
    send_user_agent: bool = field(default=DEFAULT_SEND_USER_AGENT, repr=False)

    _session: Optional[ClientSession] = field(default=None, repr=False, init=False)

    def __attrs_post_init__(self) -> None:
        add_client(self)

    def __hash__(self) -> int:
        return id(self)

    def change(self: C, **attributes: Any) -> HTTPClientContextManager[C]:
        return HTTPClientContextManager(self, attributes)

    def create_timeout(self) -> ClientTimeout:
        return ClientTimeout(total=self.timeout)

    async def close(self) -> None:
        session = self._session

        if session is not None:
            await session.close()

            self._session = None

    async def create_session(self) -> ClientSession:
        return ClientSession(skip_auto_headers=self.SKIP_HEADERS)

    async def ensure_session(self) -> None:
        session = self._session

        if self._session is None:
            self._session = session = await self.create_session()

        loop = get_running_loop()

        optional_loop = get_attribute(session, LOOP, None)

        if optional_loop is not loop:
            await self.close()

            self._session = await self.create_session()

    async def download(
        self,
        file: BinaryIO,
        url: URLString,
        method: str = GET,
        chunk_size: int = CHUNK_SIZE,
        with_bar: bool = DEFAULT_WITH_BAR,
        **request_keywords: Any,
    ) -> None:
        await self.ensure_session()

        session = self._session

        async with session.request(  # type: ignore
            url=url, method=method, **request_keywords
        ) as response:
            if with_bar:
                bar = progress(total=response.content_length, unit=UNIT, unit_scale=UNIT_SCALE)

            while True:
                chunk = await response.content.read(chunk_size)

                if not chunk:
                    break

                await run_blocking(file.write, chunk)

                if with_bar:
                    bar.update(len(chunk))

            if with_bar:
                bar.close()

    async def download_to(
        self,
        path: IntoPath,
        url: URLString,
        method: str = GET,
        chunk_size: int = CHUNK_SIZE,
        with_bar: bool = DEFAULT_WITH_BAR,
        **request_keywords: Any,
    ) -> None:
        with Path(path).open(WRITE_BINARY) as file:
            await self.download(
                file,
                url=url,
                method=method,
                chunk_size=chunk_size,
                with_bar=with_bar,
                **request_keywords,
            )

    async def download_bytes(
        self,
        url: URLString,
        method: str = GET,
        chunk_size: int = CHUNK_SIZE,
        with_bar: bool = DEFAULT_WITH_BAR,
        **request_keywords: Any,
    ) -> bytes:
        file = BytesIO()

        await self.download(
            file,
            url=url,
            method=method,
            chunk_size=chunk_size,
            with_bar=with_bar,
            **request_keywords,
        )

        file.seek(0)

        data = file.read()

        file.close()

        return data

    @overload
    async def request_route(
        self,
        route: Route,
        type: Literal[ResponseType.TEXT] = ...,
        data: Optional[Parameters] = None,
        parameters: Optional[Parameters] = None,
        error_codes: Optional[ErrorCodes] = ...,
        headers: Optional[Headers] = ...,
        base: Optional[URLString] = ...,
        retries: int = ...,
    ) -> str:
        ...

    @overload
    async def request_route(
        self,
        route: Route,
        type: Literal[ResponseType.BYTES],
        data: Optional[Parameters] = None,
        parameters: Optional[Parameters] = None,
        error_codes: Optional[ErrorCodes] = ...,
        headers: Optional[Headers] = ...,
        base: Optional[URLString] = ...,
        retries: int = ...,
    ) -> bytes:
        ...

    @overload
    async def request_route(
        self,
        route: Route,
        type: Literal[ResponseType.JSON],
        data: Optional[Parameters] = ...,
        parameters: Optional[Parameters] = ...,
        error_codes: Optional[ErrorCodes] = ...,
        headers: Optional[Headers] = ...,
        base: Optional[URLString] = ...,
        retries: int = ...,
    ) -> JSON:
        ...

    async def request_route(
        self,
        route: Route,
        type: ResponseType = ResponseType.DEFAULT,
        data: Optional[Parameters] = None,
        parameters: Optional[Parameters] = None,
        error_codes: Optional[ErrorCodes] = None,
        headers: Optional[Headers] = None,
        base: Optional[URLString] = None,
        retries: int = DEFUALT_RETRIES,
    ) -> ResponseData:
        url = URL(self.url if base is None else base)

        return await self.request(  # type: ignore
            method=route.method,
            url=url / route.route.strip(SLASH),
            type=type,
            data=data,
            parameters=parameters,
            error_codes=error_codes,
            headers=headers,
            retries=retries,
        )

    @overload
    async def request(  # type: ignore
        self,
        method: str,
        url: URLString,
        type: Literal[ResponseType.TEXT] = ...,
        read: Literal[True] = ...,
        data: Optional[Parameters] = ...,
        parameters: Optional[Parameters] = ...,
        error_codes: Optional[ErrorCodes] = ...,
        headers: Optional[Headers] = ...,
        retries: int = ...,
    ) -> str:
        ...

    @overload
    async def request(  # type: ignore
        self,
        method: str,
        url: URLString,
        type: Literal[ResponseType.BYTES],
        read: Literal[True] = ...,
        data: Optional[Parameters] = ...,
        parameters: Optional[Parameters] = ...,
        error_codes: Optional[ErrorCodes] = ...,
        headers: Optional[Headers] = ...,
        retries: int = ...,
    ) -> bytes:
        ...

    @overload
    async def request(  # type: ignore
        self,
        method: str,
        url: URLString,
        type: Literal[ResponseType.JSON],
        read: Literal[True] = ...,
        data: Optional[Parameters] = ...,
        parameters: Optional[Parameters] = ...,
        error_codes: Optional[ErrorCodes] = ...,
        headers: Optional[Headers] = ...,
        retries: int = ...,
    ) -> JSON:
        ...

    @overload
    async def request(
        self,
        method: str,
        url: URLString,
        type: ResponseType = ...,
        read: Literal[False] = ...,
        data: Optional[Parameters] = ...,
        parameters: Optional[Parameters] = ...,
        error_codes: Optional[ErrorCodes] = ...,
        headers: Optional[Headers] = ...,
        retries: int = ...,
    ) -> None:
        ...

    async def request(
        self,
        method: str,
        url: URLString,
        type: ResponseType = ResponseType.DEFAULT,
        read: bool = DEFAULT_READ,
        data: Optional[Parameters] = None,
        parameters: Optional[Parameters] = None,
        error_codes: Optional[ErrorCodes] = None,
        headers: Optional[Headers] = None,
        retries: int = DEFUALT_RETRIES,
    ) -> Optional[ResponseData]:
        await self.ensure_session()

        if retries < 0:
            attempts = -1

        else:
            attempts = retries + 1

        if headers is None:
            headers = {}

        else:
            headers = dict(headers)

        if self.send_user_agent:
            headers.setdefault(USER_AGENT, self.USER_AGENT)

        forwarded_for = self.forwarded_for

        if forwarded_for:
            headers.setdefault(FORWARDED_FOR, forwarded_for)

        lock = Lock()
        error: Optional[AnyError] = None

        utf_8 = UTF_8

        while attempts:
            try:
                async with lock, self._session.request(  # type: ignore
                    url=url,
                    method=method,
                    data=data,
                    params=parameters,
                    proxy=self.proxy,
                    proxy_auth=self.proxy_auth,
                    headers=headers,
                    timeout=self.create_timeout(),
                ) as response:
                    if not read:
                        return None

                    if type is ResponseType.BYTES:
                        response_data = await response.read()

                    elif type is ResponseType.TEXT:
                        response_data = await response.text(encoding=utf_8)

                    elif type is ResponseType.JSON:
                        response_data = await response.json(content_type=None)

                    else:
                        raise ValueError  # TODO: message?

                    status = response.status

                    if HTTP_SUCCESS <= status < HTTP_REDIRECT:
                        if error_codes:
                            if is_bytes(response_data) or is_string(response_data):
                                error_code = try_parse_error_code(response_data)

                                if error_code:
                                    raise error_codes.get(
                                        error_code, unexpected_error_code(error_code)
                                    )

                        return response_data

                    if status >= HTTP_ERROR:
                        error = HTTPStatusError(status)

            except VALID_ERRORS as valid_error:
                error = HTTPErrorWithOrigin(valid_error)

            finally:
                await sleep(0)  # let underlying connections close

            attempts -= 1

        if error:
            raise error

        return None

    @staticmethod
    def generate_udid(
        prefix: str = UDID_PREFIX, start: int = UDID_START, stop: int = UDID_STOP
    ) -> str:
        return prefix + str(get_random_range(start, stop))

    @staticmethod
    def generate_uuid() -> str:
        return str(generate_uuid())

    @staticmethod
    def generate_random_value(start: int = VALUE_START, stop: int = VALUE_STOP) -> int:
        return get_random_range(start, stop)

    def get_game_version(self) -> int:
        return self.game_version.to_robtop_value()

    def get_binary_version(self) -> int:
        return self.binary_version.to_value()

    def get_gd_world(self) -> int:
        return int(self.gd_world)

    async def ping(self, url: URLString) -> Duration:
        timer = now()

        try:
            await self.request(GET, url, read=False)

        except NormalError:
            pass

        return timer.elapsed()

    async def login(self, name: str, password: str) -> str:
        error_codes = {
            -1: LoginFailed(name, password_str(password)),
            -8: MissingAccess(NAME_TOO_SHORT),
            -9: MissingAccess(PASSWORD_TOO_SHORT),
            -10: MissingAccess(LINKED_TO_DIFFERENT),
            -11: MissingAccess(
                INCORRECT_CREDENTIALS.format(tick(name), tick(password_str(password)))
            ),
            -12: MissingAccess(ACCOUNT_DISABLED.format(tick(name))),
            -13: MissingAccess(LINKED_TO_DIFFERENT_STEAM),
        }

        route = Route(POST, LOGIN)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            user_name=name,
            password=password,
            udid=self.generate_udid(),
            secret=Secret.USER.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def load(self, *, account_id: int, name: str, password: str) -> str:
        error_codes = {
            -11: MissingAccess(
                INCORRECT_CREDENTIALS.format(tick(name), tick(password_str(password)))
            )
        }

        route = Route(POST, LOAD)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            user_name=name,
            password=password,
            secret=Secret.USER.value,
            to_camel=True,
        )

        base = await self.get_account_url(account_id, type=AccountURLType.LOAD)

        response = await self.request_route(route, data=payload, error_codes=error_codes, base=base)

        return response

    async def save(self, data: str, *, account_id: int, name: str, password: str) -> int:
        incorrect_credentials = MissingAccess(
            INCORRECT_CREDENTIALS.format(tick(name), tick(password_str(password)))
        )

        error_codes = {
            -2: incorrect_credentials,
            -4: MissingAccess(DATA_TOO_LARGE),
            -5: incorrect_credentials,
            -6: MissingAccess(SOMETHING_WENT_WRONG),
        }

        route = Route(POST, SAVE)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            save_data=data,
            user_name=name,
            password=password,
            secret=Secret.USER.value,
            to_camel=True,
        )

        base = await self.get_account_url(account_id, type=AccountURLType.SAVE)

        response = await self.request_route(route, data=payload, error_codes=error_codes, base=base)

        return int_or(response, 0)

    async def get_account_url(self, account_id: int, type: AccountURLType) -> URL:
        error_codes = {
            -1: MissingAccess(FAILED_TO_FIND_URL.format(tick(type.name), tick(account_id)))
        }

        route = Route(POST, GET_ACCOUNT_URL)

        payload = Payload(
            account_id=account_id,
            type=type.value,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        url = URL(response) / DATABASE

        return url

    async def get_role_id(self, account_id: int, encoded_password: str) -> int:
        error_codes = {-1: MissingAccess(NO_ROLE_FOUND)}

        route = Route(POST, GET_ROLE_ID)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def update_settings(
        self,
        message_state: MessageState,
        friend_request_state: FriendRequestState,
        comment_state: CommentState,
        youtube: Optional[str],
        twitter: Optional[str],
        twitch: Optional[str],
        # discord: Optional[str],
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_UPDATE_SETTINGS)}

        if youtube is None:
            youtube = EMPTY

        if twitter is None:
            twitter = EMPTY

        if twitch is None:
            twitch = EMPTY

        # if discord is None:
        #     discord = EMPTY

        route = Route(POST, UPDATE_SETTINGS)

        payload = Payload(
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.USER.value,
            m_s=message_state.value,
            fr_s=friend_request_state.value,
            c_s=comment_state.value,
            yt=youtube,
            twitter=twitter,
            twitch=twitch,
            # discord=discord,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def update_profile(
        self,
        stars: int,
        diamonds: int,
        secret_coins: int,
        user_coins: int,
        demons: int,
        icon_type: IconType,
        icon_id: int,
        color_1_id: int,
        color_2_id: int,
        glow: bool,
        cube_id: int,
        ship_id: int,
        ball_id: int,
        ufo_id: int,
        wave_id: int,
        robot_id: int,
        spider_id: int,
        # swing_copter_id: int,
        explosion_id: int,
        special: int = DEFAULT_SPECIAL,
        *,
        account_id: int,
        name: str,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(FAILED_TO_UPDATE_PROFILE.format(account_id)),
        }
        random_string = generate_random_string()

        values = (
            str(account_id),
            str(user_coins),
            str(demons),
            str(stars),
            str(secret_coins),
            str(icon_type.value),
            str(icon_id),
            str(diamonds),
            str(cube_id),
            str(ship_id),
            str(ball_id),
            str(ufo_id),
            str(wave_id),
            str(robot_id),
            bool_str(glow),
            str(spider_id),
            str(explosion_id),
        )

        check = generate_check(values, Key.USER_LEADERBOARD, Salt.USER_LEADERBOARD)

        route = Route(POST, UPDATE_PROFILE)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            stars=stars,
            diamonds=diamonds,
            coins=secret_coins,
            user_coins=user_coins,
            demons=demons,
            special=special,
            icon=icon_id,
            icon_type=icon_type.value,
            acc_icon=cube_id,
            acc_ship=ship_id,
            acc_ball=ball_id,
            acc_bird=ufo_id,
            acc_dart=wave_id,
            acc_robot=robot_id,
            acc_spider=spider_id,
            acc_explosion=explosion_id,
            acc_glow=int(glow),
            color1=color_1_id,
            color2=color_2_id,
            user_name=name,
            account_id=account_id,
            gjp=encoded_password,
            seed=random_string,
            seed2=check,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def search_users_on_page(self, query: IntString, page: int = DEFAULT_PAGE) -> str:
        error_codes = {-1: MissingAccess(CAN_NOT_FIND_USERS.format(tick(query)))}

        route = Route(POST, GET_USERS)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            str=query,
            total=NO_TOTAL,
            page=page,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_user_profile(
        self,
        account_id: int,
        *,
        client_account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> str:
        error_codes = {-1: MissingAccess(CAN_NOT_FIND_USER.format(account_id))}

        route = Route(POST, GET_USER)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if client_account_id is not None and encoded_password is not None:
            payload.update(account_id=client_account_id, gjp=encoded_password, to_camel=True)

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_relationships(
        self, type: RelationshipType, *, account_id: int, encoded_password: str
    ) -> str:
        error_codes = {
            -1: MissingAccess(CAN_NOT_FIND_USERS),
            -2: NothingFound(USERS),
        }

        route = Route(POST, GET_RELATIONSHIPS)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            type=type.value,
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_leaderboard(
        self,
        strategy: LeaderboardStrategy,
        count: int = DEFAULT_COUNT,
        *,
        account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> str:
        error_codes = {
            -1: MissingAccess(FAILED_TO_FIND_LEADERBOARD.format(tick(strategy.name.casefold())))
        }

        route = Route(POST, GET_LEADERBOARD)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            type=strategy.name.casefold(),
            count=count,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if strategy.requires_login():
            if account_id is None or encoded_password is None:
                raise LoginRequired(
                    STRATEGY_LEADERBOARD_REQUIRES_LOGIN.format(tick(strategy.name.casefold()))
                )

            payload.update(account_id=account_id, gjp=encoded_password, to_camel=True)

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def search_levels_on_page(
        self,
        query: Optional[MaybeIterable[IntString]] = None,
        page: int = DEFAULT_PAGE,
        filters: Optional[Filters] = None,
        user_id: Optional[int] = None,
        gauntlet: Optional[int] = None,
        *,
        client_account_id: Optional[int] = None,
        client_user_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> str:
        error_codes = {-1: NothingFound(LEVELS)}

        if filters is None:
            filters = Filters()

        if query is None:
            query = EMPTY

        if not is_string(query) and is_iterable(query):  # type: ignore
            query = iter(query).map(str).collect(concat_comma)

        route = Route(POST, GET_LEVELS)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if gauntlet is not None:
            payload.update(gauntlet=gauntlet)

        else:
            total = 0

            payload.update(
                filters.to_robtop_filters(), str=query, page=page, total=total, to_camel=True
            )

            if filters.strategy.is_by_user():
                if user_id is None:
                    if (
                        client_account_id is None
                        or client_user_id is None
                        or encoded_password is None
                    ):
                        raise LoginRequired(BY_USER_STRATEGY_REQUIRES_LOGIN)

                    payload.update(
                        account_id=client_account_id,
                        str=client_user_id,
                        gjp=encoded_password,
                        local=int(True),
                    )

                else:
                    payload.update(str=user_id)

            elif filters.strategy.is_friends():
                if client_account_id is None or encoded_password is None:
                    raise MissingAccess(FRIENDS_STRATEGY_REQUIRES_LOGIN)

                payload.update(account_id=client_account_id, gjp=encoded_password)

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_timely_info(self, type: TimelyType) -> str:
        error_codes = {-1: MissingAccess(CAN_NOT_FIND_TIMELY.format(tick(type.name.casefold())))}

        if type.is_not_timely():
            raise MissingAccess(EXPECTED_TIMELY)

        route = Route(POST, GET_TIMELY)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            weekly=int(type.is_weekly()),
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_level(
        self,
        level_id: int,
        *,
        account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> str:
        error_codes = {-1: MissingAccess(CAN_NOT_GET_LEVEL.format(level_id))}

        route = Route(POST, GET_LEVEL)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if account_id is not None and encoded_password is not None:
            increment = 1

            random_string = generate_random_string()

            udid = self.generate_udid()
            uuid = self.generate_uuid()

            values = (
                str(level_id),
                str(increment),
                random_string,
                str(account_id),
                udid,
                uuid,
            )

            check = generate_check(values, Key.LEVEL, Salt.LEVEL)

            payload.update(
                account_id=account_id,
                gjp=encoded_password,
                udid=udid,
                uuid=uuid,
                rs=random_string,
                chk=check,
                to_camel=True,
            )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def report_level(self, level_id: int) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_REPORT_LEVEL.format(level_id))}

        route = Route(POST, REPORT_LEVEL)

        payload = Payload(level_id=level_id, to_camel=True)

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def delete_level(self, level_id: int, *, account_id: int, encoded_password: str) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_DELETE_LEVEL.format(level_id))}

        route = Route(POST, DELETE_LEVEL)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.LEVEL.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def update_level_description(
        self, level_id: int, description: Optional[str], *, account_id: int, encoded_password: str
    ) -> int:
        error_codes = {-1: MissingAccess(CAN_NOT_UPDATE_LEVEL_DESCRIPTION.format(level_id))}

        if description is None:
            description = EMPTY

        route = Route(POST, UPDATE_LEVEL_DESCRIPTION)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            account_id=account_id,
            gjp=encoded_password,
            level_desc=encode_base64_string_url_safe(description),
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def upload_level(
        self,
        name: str = UNNAMED,
        id: int = DEFAULT_ID,
        version: int = DEFAULT_VERSION,
        length: LevelLength = LevelLength.DEFAULT,
        official_song_id: int = DEFAULT_ID,
        song_id: int = DEFAULT_ID,
        description: str = EMPTY,
        original_id: int = DEFAULT_ID,
        two_player: bool = DEFAULT_TWO_PLAYER,
        privacy: LevelPrivacy = LevelPrivacy.DEFAULT,
        object_count: int = DEFAULT_OBJECT_COUNT,
        coins: int = DEFAULT_COINS,
        stars: int = DEFAULT_STARS,
        low_detail: bool = DEFAULT_LOW_DETAIL,
        capacity: Optional[Capacity] = None,
        password: Optional[Password] = None,
        recording: Optional[Recording] = None,
        editor_time: Optional[Duration] = None,
        copies_time: Optional[Duration] = None,
        data: str = EMPTY,
        *,
        account_id: int,
        account_name: str,
        encoded_password: str,
    ) -> int:
        if editor_time is None:
            editor_time = duration()

        if copies_time is None:
            copies_time = duration()

        if capacity is None:
            capacity = Capacity()

        error_codes = {-1: MissingAccess(FAILED_TO_UPLOAD_LEVEL)}

        object_separator = OBJECT_SEPARATOR

        if object_separator in data:
            object_count = data.count(object_separator)

            data = zip_level_string(data)

        description = encode_base64_string_url_safe(description)

        extra_string = capacity.to_robtop()

        level_seed = generate_level_seed(data)

        random_string = generate_random_string()

        seed = generate_check(unary_tuple(str(level_seed)), Key.LEVEL, Salt.LEVEL)

        if recording is None:
            recording = Recording()

        recording_string = zip_level_string(recording.to_robtop())

        if password is None:
            password = Password()

        route = Route(POST, UPLOAD_LEVEL)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=id,
            level_name=name,
            level_desc=description,
            level_version=version,
            level_length=length.value,
            audio_track=official_song_id,
            song_id=song_id,
            auto=max(0, min(1, stars)),
            original=original_id,
            two_player=int(two_player),
            objects=object_count,
            coins=coins,
            requested_stars=stars,
            unlisted=int(not privacy.is_public()),
            unlisted2=int(privacy.is_friends()),
            ldm=int(low_detail),
            password=password.to_robtop_value(),
            level_string=data,
            extra_string=extra_string,
            level_info=recording_string,
            seed=random_string,
            seed2=seed,
            wt=int(editor_time.total_seconds()),  # type: ignore
            wt2=int(copies_time.total_seconds()),  # type: ignore
            account_id=account_id,
            user_name=account_name,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def rate_level(
        self, level_id: int, stars: int, *, account_id: int, encoded_password: str
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_RATE_LEVEL.format(level_id))}

        udid = self.generate_udid()
        uuid = self.generate_uuid()

        random_string = generate_random_string()

        values = (str(level_id), str(stars), random_string, str(account_id), udid, uuid)

        check = generate_check(values, Key.LIKE_RATE, Salt.LIKE_RATE)

        route = Route(POST, RATE_LEVEL)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            stars=stars,
            udid=udid,
            uuid=uuid,
            rs=random_string,
            chk=check,
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def apply_demon(
        self,
        level_id: int,
        rating: DemonDifficulty,
        as_mod: bool,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(FAILED_TO_RATE_DEMON.format(level_id)),
            -2: MissingAccess(RATE_DEMON_MISSING_PERMISSIONS.format(level_id)),
        }

        route = Route(POST, RATE_DEMON)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            rating=rating.value,
            mode=int(as_mod),
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MOD.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def rate_demon(
        self,
        level_id: int,
        rating: DemonDifficulty,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        return await self.apply_demon(
            level_id=level_id,
            rating=rating,
            as_mod=False,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def suggest_demon(
        self,
        level_id: int,
        rating: DemonDifficulty,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        return await self.apply_demon(
            level_id=level_id,
            rating=rating,
            as_mod=True,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def suggest_level(
        self,
        level_id: int,
        stars: int,
        feature: bool,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(FAILED_TO_SUGGEST_LEVEL.format(level_id)),
            -2: MissingAccess(SUGGEST_LEVEL_MISSING_PERMISSIONS.format(level_id)),
        }

        route = Route(POST, SUGGEST_LEVEL)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            stars=stars,
            feature=int(feature),
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MOD.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def get_level_leaderboard(
        self,
        level_id: int,
        strategy: LevelLeaderboardStrategy,
        timely_type: TimelyType = TimelyType.DEFAULT,
        timely_id: int = DEFAULT_ID,
        record: int = DEFAULT_RECORD,
        clicks: int = DEFAULT_CLICKS,
        attempts: int = DEFAULT_ATTEMPTS,
        seconds: int = DEFAULT_SECONDS,
        coins: int = DEFAULT_COINS,
        check: bool = DEFAULT_CHECK,
        progress: Optional[Progress] = None,
        send: bool = DEFAULT_SEND,
        *,
        account_id: int,
        encoded_password: str,
    ) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_LEADERBOARD.format(level_id))}

        route = Route(POST, GET_LEVEL_LEADERBOARD)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            account_id=account_id,
            gjp=encoded_password,
            type=strategy.value,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if send:
            if progress is None:
                progress = Progress()

            progress_string = progress.to_robtop()

            seed = generate_leaderboard_seed(clicks, record, seconds, check)

            if timely_type.is_weekly():
                timely_id += WEEKLY_ID_ADD

            random_string = generate_random_string()

            unknown = 1

            values = (  # TODO: we need to figure out if this is correct
                str(account_id),
                str(level_id),
                str(record),
                str(seconds),
                str(clicks),
                str(attempts),
                progress_string,
                str(unknown),
                str(coins),
                str(timely_id),
                random_string,
            )

            generated_check = generate_check(values, Key.LEVEL_LEADERBOARD, Salt.LEVEL_LEADERBOARD)

            payload.update(
                percent=record,
                s1=attempts + ATTEMPTS_ADD,
                s2=clicks + CLICKS_ADD,
                s3=seconds + SECONDS_ADD,
                s4=seed,
                s5=self.generate_random_value(),
                s6=encode_robtop_string(progress.to_robtop(), Key.LEVEL),
                s7=random_string,
                s8=attempts,
                s9=coins + COINS_ADD,
                s10=timely_id,
                chk=generated_check,
                to_camel=True,
            )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def block_user(
        self,
        account_id: int,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_BLOCK_USER.format(account_id))}

        route = Route(POST, BLOCK_USER)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def unblock_user(
        self,
        account_id: int,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_UNBLOCK_USER.format(account_id))}

        route = Route(POST, BLOCK_USER)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def unfriend_user(
        self, account_id: int, *, client_account_id: int, encoded_password: str
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_UNFRIEND_USER.format(account_id))}

        route = Route(POST, UNFRIEND_USER)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def send_message(
        self,
        account_id: int,
        subject: Optional[str] = None,
        content: Optional[str] = None,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_SEND_MESSAGE.format(account_id))}

        if subject is None:
            subject = EMPTY

        if content is None:
            content = EMPTY

        route = Route(POST, SEND_MESSAGE)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            subject=encode_base64_string_url_safe(subject),
            body=encode_robtop_string(content, Key.MESSAGE),
            to_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def get_message(
        self,
        message_id: int,
        type: MessageType,
        *,
        account_id: int,
        encoded_password: str,
    ) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_MESSAGE.format(message_id))}

        route = Route(POST, GET_MESSAGE)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            account_id=account_id,
            message_id=message_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if type.is_outgoing():
            payload.update(is_sender=int(True), to_camel=True)

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def delete_message(
        self,
        message_id: int,
        type: MessageType,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_DELETE_MESSAGE.format(message_id))}

        route = Route(POST, DELETE_MESSAGE)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            account_id=account_id,
            message_id=message_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if type.is_outgoing():
            payload.update(is_sender=int(True), to_camel=True)

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def get_messages_on_page(
        self, type: MessageType, page: int, *, account_id: int, encoded_password: str
    ) -> str:
        error_codes = {
            -1: MissingAccess(FAILED_TO_GET_MESSAGES.format(page)),
            -2: NothingFound(MESSAGES),
        }

        route = Route(POST, GET_MESSAGES)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            total=NO_TOTAL,
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if type.is_outgoing():
            payload.update(get_sent=int(True), to_camel=True)

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def send_friend_request(
        self,
        account_id: int,
        message: Optional[str] = None,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_SEND_FRIEND_REQUEST.format(account_id))}

        if message is None:
            message = EMPTY

        route = Route(POST, SEND_FRIEND_REQUEST)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            comment=encode_base64_string_url_safe(message),
            to_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        if not response:
            return 1

        return int_or(response, 0)

    async def delete_friend_request(
        self,
        account_id: int,
        type: FriendRequestType,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_DELETE_FRIEND_REQUEST.format(account_id))}

        route = Route(POST, DELETE_FRIEND_REQUEST)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if type.is_outgoing():
            payload.update(is_sender=int(True), to_camel=True)

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def accept_friend_request(
        self,
        account_id: int,
        request_id: int,
        type: FriendRequestType,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_ACCEPT_FRIEND_REQUEST.format(account_id))}

        route = Route(POST, ACCEPT_FRIEND_REQUEST)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            request_id=request_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if type.is_outgoing():
            payload.update(is_sender=int(True), to_camel=True)

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def read_friend_request(
        self, request_id: int, *, account_id: int, encoded_password: str
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_READ_FRIEND_REQUEST.format(request_id))}

        route = Route(POST, READ_FRIEND_REQUEST)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            request_id=request_id,
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def get_friend_requests_on_page(
        self,
        type: FriendRequestType,
        page: int,
        *,
        account_id: int,
        encoded_password: str,
    ) -> str:
        error_codes = {
            -1: MissingAccess(FAILED_TO_GET_FRIEND_REQUESTS.format(page)),
            -2: NothingFound(FRIEND_REQUESTS),
        }

        total = 0

        route = Route(POST, GET_FRIEND_REQUESTS)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            total=total,
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if type.is_outgoing():
            payload.update(get_sent=int(True), to_camel=True)

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def like_level(
        self,
        level_id: int,
        dislike: bool = False,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_LIKE_LEVEL.format(level_id))}

        like = not dislike
        special_id = 0

        type = LikeType.LEVEL

        udid = self.generate_udid()
        uuid = self.generate_uuid()

        random_string = generate_random_string()

        values = (
            str(special_id),
            str(level_id),
            bool_str(like),
            str(type.value),
            random_string,
            str(account_id),
            udid,
            uuid,
        )

        check = generate_check(values, Key.LIKE_RATE, Salt.LIKE_RATE)

        route = Route(POST, LIKE_LEVEL)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            item_id=level_id,
            type=type.value,
            special=special_id,
            like=int(like),
            account_id=account_id,
            gjp=encoded_password,
            udid=udid,
            uuid=uuid,
            rs=random_string,
            chk=check,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def like_user_comment(
        self,
        comment_id: int,
        dislike: bool = False,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_LIKE_USER_COMMENT.format(comment_id))}

        like = not dislike
        special_id = comment_id

        type = LikeType.USER_COMMENT

        udid = self.generate_udid()
        uuid = self.generate_uuid()

        random_string = generate_random_string()

        values = (
            str(special_id),
            str(comment_id),
            bool_str(like),
            str(type.value),
            random_string,
            str(account_id),
            udid,
            uuid,
        )

        check = generate_check(values, Key.LIKE_RATE, Salt.LIKE_RATE)

        route = Route(POST, LIKE_USER_COMMENT)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            item_id=comment_id,
            type=type.value,
            special=special_id,
            like=int(like),
            account_id=account_id,
            gjp=encoded_password,
            udid=udid,
            uuid=uuid,
            rs=random_string,
            chk=check,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def like_level_comment(
        self,
        comment_id: int,
        level_id: int,
        dislike: bool = False,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_LIKE_LEVEL_COMMENT.format(comment_id))}

        like = not dislike
        special_id = level_id

        type = LikeType.LEVEL_COMMENT

        udid = self.generate_udid()
        uuid = self.generate_uuid()

        random_string = generate_random_string()

        values = (
            str(special_id),
            str(comment_id),
            bool_str(like),
            str(type.value),
            random_string,
            str(account_id),
            udid,
            uuid,
        )

        check = generate_check(values, Key.LIKE_RATE, Salt.LIKE_RATE)

        route = Route(POST, LIKE_LEVEL_COMMENT)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            item_id=comment_id,
            type=type.value,
            special=special_id,
            like=int(like),
            account_id=account_id,
            gjp=encoded_password,
            udid=udid,
            uuid=uuid,
            rs=random_string,
            chk=check,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def post_user_comment(
        self,
        content: Optional[str] = None,
        *,
        account_id: int,
        account_name: str,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(FAILED_TO_POST_USER_COMMENT),
            -10: CommentBanned(),
        }

        if content is None:
            content = EMPTY

        content = encode_base64_string_url_safe(content)

        level_id = 0
        record = 0

        type = CommentType.USER

        values = (account_name, content, str(level_id), str(record), str(type.value))

        check = generate_check(values, Key.COMMENT, Salt.COMMENT)

        route = Route(POST, POST_USER_COMMENT)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            comment=content,
            c_type=type.value,
            account_id=account_id,
            user_name=account_name,
            gjp=encoded_password,
            chk=check,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        if CommentBannedModel.can_be_in(response):
            ban = CommentBannedModel.from_robtop(response)

            raise CommentBanned(timeout=ban.timeout, reason=ban.reason)

        return int_or(response, 0)

    async def post_level_comment(
        self,
        level_id: int,
        content: Optional[str],
        record: int,
        *,
        account_id: int,
        account_name: str,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(FAILED_TO_POST_LEVEL_COMMENT.format(level_id)),
            -10: CommentBanned(),
        }

        if content is None:
            content = EMPTY

        content = encode_base64_string_url_safe(content)

        type = CommentType.LEVEL

        values = (account_name, content, str(level_id), str(record), str(type.value))

        check = generate_check(values, Key.COMMENT, Salt.COMMENT)

        route = Route(POST, POST_USER_COMMENT)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            comment=content,
            level_id=level_id,
            c_type=type.value,
            percent=record,
            account_id=account_id,
            user_name=account_name,
            gjp=encoded_password,
            chk=check,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        if CommentBannedModel.can_be_in(response):
            ban = CommentBannedModel.from_robtop(response)

            raise CommentBanned(timeout=ban.timeout, reason=ban.reason)

        return int_or(response, 0)

    async def delete_user_comment(
        self,
        comment_id: int,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_DELETE_USER_COMMENT.format(comment_id))}

        type = CommentType.USER

        level_id = 0

        route = Route(POST, DELETE_USER_COMMENT)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            comment_id=comment_id,
            c_type=type.value,
            level_id=level_id,
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def delete_level_comment(
        self,
        comment_id: int,
        level_id: int,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_DELETE_LEVEL_COMMENT.format(comment_id))}

        type = CommentType.LEVEL

        route = Route(POST, DELETE_LEVEL_COMMENT)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            comment_id=comment_id,
            c_type=type.value,
            level_id=level_id,
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return int_or(response, 0)

    async def get_user_comments_on_page(
        self,
        account_id: int,
        page: int = DEFAULT_PAGE,
    ) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_USER_COMMENTS.format(account_id))}

        route = Route(POST, GET_USER_COMMENTS)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            total=NO_TOTAL,
            account_id=account_id,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_user_level_comments_on_page(
        self,
        user_id: int,
        count: int,
        page: int = DEFAULT_PAGE,
        strategy: CommentStrategy = CommentStrategy.DEFAULT,
    ) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_USER_LEVEL_COMMENTS.format(user_id))}

        route = Route(POST, GET_USER_LEVEL_COMMENTS)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            count=count,
            total=NO_TOTAL,
            mode=strategy.value,
            user_id=user_id,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_level_comments_on_page(
        self,
        level_id: int,
        count: int,
        page: int = DEFAULT_PAGE,
        *,
        strategy: CommentStrategy,
    ) -> str:
        error_codes = {
            -1: MissingAccess(FAILED_TO_GET_LEVEL_COMMENTS.format(level_id)),
            -2: NothingFound(LEVEL_COMMENTS),
        }

        route = Route(POST, GET_LEVEL_COMMENTS)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            page=page,
            total=NO_TOTAL,
            count=count,
            mode=strategy.value,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_gauntlets(self) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_GAUNTLETS)}

        route = Route(POST, GET_GAUNTLETS)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_map_packs_on_page(self, page: int = DEFAULT_PAGE) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_MAP_PACKS)}

        route = Route(POST, GET_MAP_PACKS)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_chests(
        self,
        reward_type: RewardType,
        chest_1_count: int = DEFAULT_CHEST_COUNT,
        chest_2_count: int = DEFAULT_CHEST_COUNT,
        *,
        account_id: int,
        encoded_password: str,
    ) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_CHESTS)}

        check = generate_random_string_and_encode_value(Key.CHESTS)

        route = Route(POST, GET_CHESTS)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            reward_type=reward_type.value,
            account_id=account_id,
            gjp=encoded_password,
            uuid=self.generate_uuid(),
            udid=self.generate_udid(),
            chk=check,
            r1=chest_1_count,
            r2=chest_2_count,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_quests(self, *, account_id: int, encoded_password: str) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_QUESTS)}

        check = generate_random_string_and_encode_value(Key.QUESTS)

        world = self.get_gd_world()

        route = Route(POST, GET_QUESTS)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=world,
            account_id=account_id,
            gjp=encoded_password,
            uuid=self.generate_uuid(),
            udid=self.generate_udid(),
            chk=check,
            world=world,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_artists_on_page(self, page: int = DEFAULT_PAGE) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_ARTISTS)}

        total = 0

        route = Route(POST, GET_ARTISTS)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            total=total,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_song(self, song_id: int) -> str:
        error_codes = {
            -1: MissingAccess(FAILED_TO_GET_SONG.format(song_id)),
            -2: SongRestricted(song_id),
        }

        route = Route(POST, GET_SONG)

        payload = Payload(
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            song_id=song_id,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, data=payload, error_codes=error_codes)

        return response

    async def get_newgrounds_song(self, song_id: int) -> str:
        response = await self.request(GET, NEWGROUNDS_SONG.format(song_id))

        return response

    async def search_newgrounds_songs_on_page(self, query: str, page: int = DEFAULT_PAGE) -> str:
        page += 1  # 1-based indexing

        response = await self.request(
            GET,
            NEWGROUNDS_SEARCH.format(AUDIO),
            parameters=dict(terms=query, page=page),
        )

        return response

    async def search_newgrounds_artists_on_page(self, query: str, page: int = DEFAULT_PAGE) -> str:
        page += 1  # 1-based indexing

        response = await self.request(
            GET,
            NEWGROUNDS_SEARCH.format(USERS),
            parameters=dict(terms=query, page=page),
        )

        return response

    async def get_newgrounds_artist_songs_on_page(
        self, artist_name: str, page: int = DEFAULT_PAGE
    ) -> Mapping[str, Any]:
        page += 1  # 1-based indexing

        response = await self.request(
            GET,
            NEWGROUNDS_SONG_PAGE.format(artist_name, page),
            type=ResponseType.JSON,
            headers={REQUESTED_WITH: XML_HTTP_REQUEST},
        )

        return response  # type: ignore


E = TypeVar("E", bound=AnyError)


@frozen()
class HTTPClientContextManager(Generic[C]):
    client: C = field()
    attributes: Namespace = field(repr=False)
    saved_attributes: Namespace = field(factory=dict, repr=False, init=False)

    def apply(self) -> None:
        client = self.client
        attributes = self.attributes
        saved_attributes = self.saved_attributes

        for attribute, value in attributes.items():
            saved_attributes[attribute] = get_attribute(client, attribute)  # store attribute values
            set_attribute(client, attribute, value)

    def discard(self) -> None:
        client = self.client
        saved_attributes = self.saved_attributes

        for saved_attribute, saved_value in saved_attributes.items():
            set_attribute(client, saved_attribute, saved_value)  # restore old attribute values

    def __enter__(self) -> C:
        self.apply()

        return self.client

    @overload
    def __exit__(self, error_type: None, error: None, traceback: None) -> None:
        ...

    @overload
    def __exit__(self, error_type: Type[E], error: E, traceback: Traceback) -> None:
        ...

    def __exit__(
        self, error_type: Optional[Type[E]], error: Optional[E], traceback: Optional[Traceback]
    ) -> None:
        self.discard()
