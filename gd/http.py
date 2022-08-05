from __future__ import annotations

from asyncio import Lock, get_running_loop, new_event_loop, set_event_loop, sleep
from atexit import register as register_at_exit
from builtins import getattr as get_attribute
from builtins import setattr as set_attribute
from datetime import timedelta
from io import BytesIO
from itertools import repeat
from pathlib import Path
from random import randrange as get_random_range
from types import TracebackType as Traceback
from typing import (
    Any,
    AnyStr,
    BinaryIO,
    ClassVar,
    Generic,
    Iterable,
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
from attrs import define, field, frozen
from tqdm import tqdm as progess  # type: ignore
from typing_extensions import Literal
from yarl import URL

from gd.api.recording import Recording
from gd.async_utils import maybe_await_call, shutdown_loop
from gd.constants import (
    BACKSLASH,
    DEFAULT_CHEST_COUNT,
    DEFAULT_COINS,
    DEFAULT_ID,
    DEFAULT_LOW_DETAIL,
    DEFAULT_OBJECTS,
    DEFAULT_PAGE,
    DEFAULT_SPECIAL,
    DEFAULT_STARS,
    DEFAULT_TIME,
    DEFAULT_VERSION,
    EMPTY,
    SLASH,
    UNKNOWN,
)
from gd.encoding import (
    ATTEMPTS_ADD,
    COINS_ADD,
    JUMPS_ADD,
    SECONDS_ADD,
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
    LikeType,
    MessageState,
    MessageType,
    ResponseType,
    RewardType,
    Salt,
    SearchStrategy,
    Secret,
    SimpleRelationshipType,
    TimelyType,
    UnlistedType,
)
from gd.errors import (
    CommentBanned,
    HTTPError,
    HTTPStatusError,
    LoginFailed,
    LoginRequired,
    MissingAccess,
    NothingFound,
    SongRestricted,
)
from gd.filters import Filters
from gd.iter_utils import tuple_args
from gd.models import CommentBannedModel
from gd.models_constants import OBJECTS_SEPARATOR
from gd.models_utils import concat_extra_string
from gd.password import Password
from gd.string_utils import concat_comma, password_str, tick
from gd.text_utils import snake_to_camel
from gd.timer import create_timer
from gd.typing import (
    AnyException,
    DynamicTuple,
    Headers,
    IntoPath,
    IntString,
    JSONType,
    MaybeAsyncUnary,
    MaybeIterable,
    Namespace,
    Parameters,
    URLString,
    is_bytes,
    is_iterable,
    is_string,
)
from gd.version import python_version_info, version_info
from gd.versions import CURRENT_BINARY_VERSION, CURRENT_GAME_VERSION, GameVersion, Version

__all__ = ("Route", "HTTPClient")

DATABASE = "database"
ROOT = "/"

BASE = "http://www.boomlings.com/database"
GD_BASE = "http://geometrydash.com/database"

NEWGROUNDS_SONG_LISTEN = "https://newgrounds.com/audio/listen/{}"
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
DOWNLOAD_LEVEL = "downloadGJLevel22.php"
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
GET_FRIEND_REQUEST = "readGJFriendRequest20.php"
GET_FRIEND_REQUESTS = "getGJFriendRequests20.php"
LIKE_ITEM = "likeGJItem211.php"
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
GET_FEATURED_ARTISTS = "getGJTopArtists.php"
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

CHUNK_SIZE = 64 * 1024

ResponseData = Union[bytes, str, JSONType]

COMMENT_ADD = 1 << 31


UNEXPECTED_ERROR_CODE = "got an unexpected error code: {}"


def unexpected_error_code(error_code: int) -> MissingAccess:
    return MissingAccess(UNEXPECTED_ERROR_CODE.format(tick(error_code)))


ID = "ID"
ID_TITLE = ID.title()


def snake_to_camel_with_id(string: str) -> str:
    return snake_to_camel(string).replace(ID_TITLE, ID)


DEFAULT_HAS_DATA = True
DEFAULT_TO_CAMEL = True

ROUTE = "{} {}"


@frozen()
class Route:
    method: str = field()
    route: str = field()
    has_data: bool = field(default=DEFAULT_HAS_DATA, kw_only=True)
    to_camel: bool = field(default=DEFAULT_TO_CAMEL, kw_only=True)
    parameters: Namespace = field(factory=dict, kw_only=True)

    def __init__(
        self,
        method: str,
        route: str,
        *,
        has_data: bool = DEFAULT_HAS_DATA,
        to_camel: bool = DEFAULT_TO_CAMEL,
        **parameters: Any,
    ) -> None:
        self.__attrs_init__(method, route, to_camel=to_camel, has_data=has_data)

        self.update(parameters, to_camel=to_camel)

    def update(
        self,
        mapping: Optional[Namespace] = None,
        *,
        to_camel: bool = DEFAULT_TO_CAMEL,
        **parameters: Any,
    ) -> None:
        if mapping is not None:
            parameters.update(mapping)

        if to_camel:
            self.parameters.update(
                {snake_to_camel_with_id(name): value for name, value in parameters.items()}
            )

        else:
            self.parameters.update(parameters)

    def __str__(self) -> str:
        return ROUTE.format(self.method, tick(self.route))


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


def try_parse_error_code(string: AnyStr) -> Optional[int]:
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

DEFAULT_CLOSE = True

DEFUALT_RETRIES = 2

DEFAULT_READ = True

UDID_PREFIX = "S"
UDID_START = 100_000
UDID_STOP = 100_000_000

EXTRA_STRING_COUNT = 55

LOOP = "_loop"  # NOTE: keep in sync with the upstream library

UNIT = "b"
UNIT_SCALE = True

WRITE_BINARY = "wb"

ErrorCodes = Mapping[int, AnyException]

H = TypeVar("H", bound="RequestHook")

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

CAN_NOT_DOWNLOAD_LEVEL = "can not download level with ID: {}"

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

FAILED_TO_GET_FRIEND_REQUEST = "failed to get the friend request (ID: {})"

FAILED_TO_GET_FRIEND_REQUESTS = "failed to get friend requests on page {}"

FAILED_TO_LIKE_ITEM = "failed to like the item (ID: {})"

FAILED_TO_POST_USER_COMMENT = "failed to post the user comment"

FAILED_TO_POST_LEVEL_COMMENT = "failed to post the level comment"

FAILED_TO_DELETE_USER_COMMENT = "failed to delete the user comment (ID: {})"

FAILED_TO_DELETE_LEVEL_COMMENT = "failed to delete the level comment (ID: {})"

FAILED_TO_GET_USER_LEVEL_COMMENTS = "failed to get user level comments (ID: {})"

FAILED_TO_GET_LEVEL_COMMENTS = "failed to get level comments (ID: {})"

FAILED_TO_GET_GAUNTLETS = "failed to get gauntlets"

FAILED_TO_GET_MAP_PACKS = "failed to get map packs on page {}"

FAILED_TO_GET_QUESTS = "failed to get quests"

FAILED_TO_GET_CHESTS = "failed to get chests"

FAILED_TO_GET_FEATURED_ARTISTS = "failed to get featured artists"

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
    binary_version: Version = field(default=CURRENT_BINARY_VERSION)
    gd_world: bool = field(default=DEFAULT_GD_WORLD)
    forwarded_for: Optional[str] = field(default=None, repr=False)
    send_user_agent: bool = field(default=DEFAULT_SEND_USER_AGENT, repr=False)

    _session: Optional[ClientSession] = field(default=None, repr=False, init=False)

    _before_request: Optional[RequestHook] = field(default=None, repr=False, init=False)
    _after_request: Optional[RequestHook] = field(default=None, repr=False, init=False)

    def __attrs_post_init__(self) -> None:
        add_client(self)

    def __hash__(self) -> int:
        return id(self)

    def change(self: C, **attributes: Any) -> HTTPClientContextManager[C]:
        return HTTPClientContextManager(self, **attributes)

    def create_timeout(self) -> ClientTimeout:
        return ClientTimeout(total=self.timeout)

    def before_request(self, request_hook: H) -> H:
        self._before_request = request_hook

        return request_hook

    def after_request(self, request_hook: H) -> H:
        self._after_request = request_hook

        return request_hook

    async def call_before_request_hook(self) -> None:
        before_request = self._before_request

        if before_request:
            await maybe_await_call(before_request, self)

    async def call_after_request_hook(self) -> None:
        after_request = self._after_request

        if after_request:
            await maybe_await_call(after_request, self)

    async def close(self) -> None:
        session = self._session

        if session:
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
        close: bool = DEFAULT_CLOSE,
        **request_keywords: Any,
    ) -> None:
        await self.ensure_session()

        session = self._session

        async with session.request(  # type: ignore
            url=url, method=method, **request_keywords
        ) as response:
            if with_bar:
                bar = progess(total=response.content_length, unit=UNIT, unit_scale=UNIT_SCALE)

            while True:
                chunk = await response.content.read(chunk_size)

                if not chunk:
                    break

                file.write(chunk)

                if with_bar:
                    bar.update(len(chunk))

            if with_bar:
                bar.close()

        if close:
            file.close()

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
            close=False,
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
        error_codes: Optional[ErrorCodes] = ...,
        headers: Optional[Headers] = ...,
        base: Optional[URLString] = ...,
        retries: int = ...,
    ) -> JSONType:
        ...

    async def request_route(
        self,
        route: Route,
        type: ResponseType = ResponseType.DEFAULT,
        error_codes: Optional[ErrorCodes] = None,
        headers: Optional[Headers] = None,
        base: Optional[URLString] = None,
        retries: int = DEFUALT_RETRIES,
    ) -> ResponseData:
        url = URL(self.url if base is None else base)

        keywords = dict(
            method=route.method,
            url=url / route.route.strip(SLASH),
            type=type,
            error_codes=error_codes,
            headers=headers,
            retries=retries,
        )

        if route.has_data:
            keywords.update(data=route.parameters)

        else:
            keywords.update(params=route.parameters)

        return await self.request(**keywords)  # type: ignore

    @overload
    async def request(
        self,
        method: str,
        url: URLString,
        type: Literal[ResponseType.TEXT] = ...,
        read: Literal[True] = ...,
        data: Optional[Parameters] = ...,
        params: Optional[Parameters] = ...,
        error_codes: Optional[ErrorCodes] = ...,
        headers: Optional[Headers] = ...,
        retries: int = ...,
    ) -> str:
        ...

    @overload
    async def request(
        self,
        method: str,
        url: URLString,
        type: Literal[ResponseType.BYTES],
        read: Literal[True] = ...,
        data: Optional[Parameters] = ...,
        params: Optional[Parameters] = ...,
        error_codes: Optional[ErrorCodes] = ...,
        headers: Optional[Headers] = ...,
        retries: int = ...,
    ) -> bytes:
        ...

    @overload
    async def request(
        self,
        method: str,
        url: URLString,
        type: Literal[ResponseType.JSON],
        read: Literal[True] = ...,
        data: Optional[Parameters] = ...,
        params: Optional[Parameters] = ...,
        error_codes: Optional[ErrorCodes] = ...,
        headers: Optional[Headers] = ...,
        retries: int = ...,
    ) -> JSONType:
        ...

    @overload
    async def request(
        self,
        method: str,
        url: URLString,
        type: ResponseType = ...,
        read: Literal[False] = ...,
        data: Optional[Parameters] = ...,
        params: Optional[Parameters] = ...,
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
        params: Optional[Parameters] = None,
        error_codes: Optional[ErrorCodes] = None,
        headers: Optional[Headers] = None,
        retries: int = DEFUALT_RETRIES,
    ) -> Optional[ResponseData]:
        await self.ensure_session()

        await self.call_before_request_hook()

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
        error: Optional[BaseException] = None

        while attempts:
            try:
                async with lock, self._session.request(  # type: ignore
                    url=url,
                    method=method,
                    data=data,
                    params=params,
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
                        response_data = await response.text()

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
                        reason = response.reason

                        error = HTTPStatusError(status, reason)

            except VALID_ERRORS as valid_error:
                error = HTTPError(valid_error)

            finally:
                await sleep(0)  # let underlying connections close

            attempts -= 1

        await self.call_after_request_hook()

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
    def generate_extra_string(count: int = EXTRA_STRING_COUNT) -> str:
        return concat_extra_string(map(str, repeat(0, count)))

    def get_game_version(self) -> int:
        return self.game_version.to_robtop_value()

    def get_binary_version(self) -> int:
        return self.binary_version.to_value()

    def get_gd_world(self) -> int:
        return int(self.gd_world)

    async def ping(self, url: Union[str, URL]) -> timedelta:
        timer = create_timer()

        try:
            await self.request(GET, url, read=False)

        except Exception:  # noqa
            pass

        return timer.elapsed()

    async def login(self, name: str, password: str) -> str:
        error_codes = {
            -1: LoginFailed(name=name, password=password),
            -8: MissingAccess(NAME_TOO_SHORT),
            -9: MissingAccess(PASSWORD_TOO_SHORT),
            -10: MissingAccess(LINKED_TO_DIFFERENT),
            -11: MissingAccess(
                INCORRECT_CREDENTIALS.format(tick(name), tick(password_str(password)))
            ),
            -12: MissingAccess(ACCOUNT_DISABLED.format(tick(name))),
            -13: MissingAccess(LINKED_TO_DIFFERENT_STEAM),
        }

        route = Route(
            POST,
            LOGIN,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            user_name=name,
            password=password,
            udid=self.generate_udid(),
            secret=Secret.USER.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def load(self, *, account_id: int, name: str, password: str) -> str:
        error_codes = {
            -11: MissingAccess(
                INCORRECT_CREDENTIALS.format(tick(name), tick(password_str(password)))
            )
        }

        route = Route(
            POST,
            LOAD,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            user_name=name,
            password=password,
            secret=Secret.USER.value,
            to_camel=True,
        )

        base = await self.get_account_url(account_id, type=AccountURLType.LOAD)

        response = await self.request_route(route, error_codes=error_codes, base=base)

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

        route = Route(
            POST,
            SAVE,
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

        response = await self.request_route(route, error_codes=error_codes, base=base)

        return int_or(response, 0)

    async def get_account_url(self, account_id: int, type: AccountURLType) -> URL:
        error_codes = {
            -1: MissingAccess(FAILED_TO_FIND_URL.format(tick(type.name), tick(account_id)))
        }

        route = Route(
            POST,
            GET_ACCOUNT_URL,
            account_id=account_id,
            type=type.value,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        url = URL(response)

        if url.path == ROOT:
            return url / DATABASE

        return url

    async def get_role_id(self, account_id: int, encoded_password: str) -> int:
        error_codes = {-1: MissingAccess(NO_ROLE_FOUND)}

        route = Route(
            POST,
            GET_ROLE_ID,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def update_settings(
        self,
        message_state: MessageState,
        friend_request_state: FriendRequestState,
        comment_state: CommentState,
        youtube: str,
        twitter: str,
        twitch: str,
        # discord: str,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_UPDATE_SETTINGS)}

        route = Route(
            POST,
            UPDATE_SETTINGS,
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

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def update_profile(
        self,
        stars: int,
        diamonds: int,
        coins: int,
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
            account_id,
            user_coins,
            demons,
            stars,
            coins,
            icon_type.value,
            icon_id,
            diamonds,
            cube_id,
            ship_id,
            ball_id,
            ufo_id,
            wave_id,
            robot_id,
            int(glow),
            spider_id,
            explosion_id,
        )

        check = generate_check(map(str, values), Key.USER_LEADERBOARD, Salt.USER_LEADERBOARD)

        route = Route(
            POST,
            UPDATE_PROFILE,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            stars=stars,
            diamonds=diamonds,
            coins=coins,
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

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def search_users_on_page(self, query: Union[int, str], page: int = DEFAULT_PAGE) -> str:
        error_codes = {-1: MissingAccess(CAN_NOT_FIND_USERS.format(tick(query)))}

        route = Route(
            POST,
            GET_USERS,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            str=query,
            total=0,
            page=page,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def get_user_profile(
        self,
        account_id: int,
        *,
        client_account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> str:
        error_codes = {-1: MissingAccess(CAN_NOT_FIND_USER.format(account_id))}

        route = Route(
            POST,
            GET_USER,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if client_account_id is not None and encoded_password is not None:
            route.update(account_id=client_account_id, gjp=encoded_password, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def get_relationships(
        self, type: SimpleRelationshipType, *, account_id: int, encoded_password: str
    ) -> str:
        error_codes = {
            -1: MissingAccess(CAN_NOT_FIND_USERS),
            -2: NothingFound(USERS),
        }

        route = Route(
            POST,
            GET_RELATIONSHIPS,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            type=type.value,
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def get_leaderboard(
        self,
        strategy: LeaderboardStrategy,
        count: int = 100,
        *,
        account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> str:
        error_codes = {
            -1: MissingAccess(FAILED_TO_FIND_LEADERBOARD.format(tick(strategy.name.casefold())))
        }

        route = Route(
            POST,
            GET_LEADERBOARD,
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

            route.update(account_id=account_id, gjp=encoded_password, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

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

        if not is_string(query) and is_iterable(query):
            query = concat_comma(map(str, query))

        route = Route(
            POST,
            GET_LEVELS,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if gauntlet is not None:
            route.update(gauntlet=gauntlet)

        else:
            total = 0

            route.update(
                filters.to_robtop_filters(), str=query, page=page, total=total, to_camel=True
            )

            if filters.strategy is SearchStrategy.BY_USER:
                if user_id is None:
                    if (
                        client_account_id is None
                        or client_user_id is None
                        or encoded_password is None
                    ):
                        raise LoginRequired(BY_USER_STRATEGY_REQUIRES_LOGIN)

                    route.update(
                        account_id=client_account_id,
                        str=client_user_id,
                        gjp=encoded_password,
                        local=1,
                    )

                else:
                    route.update(str=user_id)

            elif filters.strategy is SearchStrategy.FRIENDS:
                if client_account_id is None or encoded_password is None:
                    raise MissingAccess(FRIENDS_STRATEGY_REQUIRES_LOGIN)

                route.update(account_id=client_account_id, gjp=encoded_password)

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def get_timely_info(self, type: TimelyType) -> str:
        error_codes = {-1: MissingAccess(CAN_NOT_FIND_TIMELY.format(tick(type.name.casefold())))}

        if type.is_not_timely():
            raise MissingAccess(EXPECTED_TIMELY)

        route = Route(
            POST,
            GET_TIMELY,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            weekly=int(type.is_weekly()),
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def download_level(
        self,
        level_id: int,
        *,
        account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> str:
        error_codes = {-1: MissingAccess(CAN_NOT_DOWNLOAD_LEVEL.format(level_id))}

        route = Route(
            POST,
            DOWNLOAD_LEVEL,
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

            values = (level_id, increment, random_string, account_id, udid, uuid)

            check = generate_check(map(str, values), Key.LEVEL, Salt.LEVEL)

            route.update(
                account_id=account_id,
                gjp=encoded_password,
                udid=udid,
                uuid=uuid,
                rs=random_string,
                chk=check,
                to_camel=True,
            )

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def report_level(self, level_id: int) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_REPORT_LEVEL.format(level_id))}

        route = Route(POST, REPORT_LEVEL, level_id=level_id, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def delete_level(self, level_id: int, *, account_id: int, encoded_password: str) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_DELETE_LEVEL.format(level_id))}

        route = Route(
            POST,
            DELETE_LEVEL,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.LEVEL.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def update_level_description(
        self, level_id: int, description: str, *, account_id: int, encoded_password: str
    ) -> int:
        error_codes = {-1: MissingAccess(CAN_NOT_UPDATE_LEVEL_DESCRIPTION.format(level_id))}

        route = Route(
            POST,
            UPDATE_LEVEL_DESCRIPTION,
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

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    # HERE

    async def upload_level(
        self,
        name: str = UNKNOWN,
        id: int = DEFAULT_ID,
        version: int = DEFAULT_VERSION,
        length: LevelLength = LevelLength.TINY,
        track_id: int = DEFAULT_ID,
        description: str = EMPTY,
        song_id: int = DEFAULT_ID,
        original: int = DEFAULT_ID,
        two_player: bool = False,
        type: UnlistedType = UnlistedType.DEFAULT,
        objects: int = DEFAULT_OBJECTS,
        coins: int = DEFAULT_COINS,
        stars: int = DEFAULT_STARS,
        low_detail: bool = DEFAULT_LOW_DETAIL,
        password: Optional[Password] = None,
        recording: Optional[Recording] = None,
        editor_time: timedelta = DEFAULT_TIME,
        copies_time: timedelta = DEFAULT_TIME,
        data: str = EMPTY,
        *,
        account_id: int,
        account_name: str,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_UPLOAD_LEVEL)}

        objects_separator = OBJECTS_SEPARATOR

        if objects_separator in data:
            if not objects:
                objects = data.count(objects_separator)

            data = zip_level_string(data)

        extra_string = self.generate_extra_string()

        description = encode_base64_string_url_safe(description)

        level_seed = generate_level_seed(data)

        random_string = generate_random_string()

        seed = generate_check(tuple_args(str(level_seed)), Key.LEVEL, Salt.LEVEL)

        if recording is None:
            recording = Recording()

        recording_string = zip_level_string(recording.to_robtop())

        if password is None:
            password = Password()

        route = Route(
            POST,
            UPLOAD_LEVEL,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=id,
            level_name=name,
            level_desc=description,
            level_version=version,
            level_length=length.value,
            audio_track=track_id,
            song_id=song_id,
            auto=max(0, min(1, stars)),
            original=original,
            two_player=int(two_player),
            objects=objects,
            coins=coins,
            requested_stars=stars,
            unlisted=type.is_unlisted(),
            unlisted2=type.is_listed_to_friends(),
            ldm=int(low_detail),
            password=password.to_robtop_value(),
            level_string=data,
            extra_string=extra_string,
            level_info=recording_string,
            seed=random_string,
            seed2=seed,
            wt=int(editor_time.total_seconds()),
            wt2=int(copies_time.total_seconds()),
            account_id=account_id,
            user_name=account_name,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def rate_level(
        self, level_id: int, stars: int, *, account_id: int, encoded_password: str
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_RATE_LEVEL.format(level_id))}

        udid = self.generate_udid()
        uuid = self.generate_uuid()

        random_string = generate_random_string()

        values = (level_id, stars, random_string, account_id, udid, uuid)

        check = generate_check(map(str, values), Key.LIKE_RATE, Salt.LIKE_RATE)

        route = Route(
            POST,
            RATE_LEVEL,
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

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def rate_demon(
        self,
        level_id: int,
        rating: DemonDifficulty,
        as_mod: bool = False,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(FAILED_TO_RATE_DEMON.format(level_id)),
            -2: MissingAccess(RATE_DEMON_MISSING_PERMISSIONS.format(level_id)),
        }

        route = Route(
            POST,
            RATE_DEMON,
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

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

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

        route = Route(
            POST,
            SUGGEST_LEVEL,
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

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def get_level_leaderboard(
        self,
        level_id: int,
        strategy: LevelLeaderboardStrategy,
        timely_type: TimelyType = TimelyType.DEFAULT,
        timely_id: int = DEFAULT_ID,
        played: bool = False,
        percentage: int = 0,
        jumps: int = 0,
        attempts: int = 0,
        seconds: int = 0,
        coins: int = 0,
        progress: Iterable[int] = (),
        send: bool = False,
        *,
        account_id: int,
        encoded_password: str,
    ) -> str:

        error_codes = {-1: MissingAccess(FAILED_TO_GET_LEADERBOARD.format(level_id))}

        seed = generate_leaderboard_seed(jumps, percentage, seconds, played)

        if timely_type is TimelyType.WEEKLY:
            timely_id += 100_000

        random_string = generate_random_string()

        unknown = 1

        values = (
            account_id,
            level_id,
            percentage,
            seconds,
            jumps,
            attempts,
            percentage,
            100 - percentage,
            unknown,
            coins,
            timely_id,
            random_string,
        )

        check = generate_check(map(str, values), Key.LEVEL_LEADERBOARD, Salt.LEVEL_LEADERBOARD)

        route = Route(
            POST,
            GET_LEVEL_LEADERBOARD,
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

        progress_string = concat_comma(map(str, progress))

        if send:
            route.update(
                percent=percentage,
                s1=attempts + ATTEMPTS_ADD,
                s2=jumps + JUMPS_ADD,
                s3=seconds + SECONDS_ADD,
                s4=seed,
                s5=get_random_range(100, 100000),
                s6=progress_string,
                s7=random_string,
                s8=attempts,
                s9=coins + COINS_ADD,
                s10=timely_id,
                chk=check,
                to_camel=True,
            )

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def block_user(
        self,
        account_id: int,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_BLOCK_USER.format(account_id))}

        route = Route(
            POST,
            BLOCK_USER,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def unblock_user(
        self,
        account_id: int,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_UNBLOCK_USER.format(account_id))}

        route = Route(
            POST,
            BLOCK_USER,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def unfriend_user(
        self, account_id: int, *, client_account_id: int, encoded_password: str
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_UNFRIEND_USER.format(account_id))}

        route = Route(
            POST,
            UNFRIEND_USER,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

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

        route = Route(
            POST,
            SEND_MESSAGE,
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

        response = await self.request_route(route, error_codes=error_codes)

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

        route = Route(
            POST,
            GET_MESSAGE,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            account_id=account_id,
            message_id=message_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if type is MessageType.OUTGOING:
            route.update(is_sender=1, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

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

        route = Route(
            POST,
            DELETE_MESSAGE,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            account_id=account_id,
            message_id=message_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if type is MessageType.OUTGOING:
            route.update(is_sender=1, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def get_messages_on_page(
        self, type: MessageType, page: int, *, account_id: int, encoded_password: str
    ) -> str:
        error_codes = {
            -1: MissingAccess(FAILED_TO_GET_MESSAGES.format(page)),
            -2: NothingFound(MESSAGES),
        }

        route = Route(
            POST,
            GET_MESSAGES,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            total=0,
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if type is MessageType.OUTGOING:
            route.update(get_sent=1, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

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

        route = Route(
            POST,
            SEND_FRIEND_REQUEST,
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

        response = await self.request_route(route, error_codes=error_codes)

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

        route = Route(
            POST,
            DELETE_FRIEND_REQUEST,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        if type is FriendRequestType.OUTGOING:
            route.update(is_sender=1, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

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

        route = Route(
            POST,
            ACCEPT_FRIEND_REQUEST,
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

        if type is FriendRequestType.OUTGOING:
            route.update(is_sender=1, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def get_friend_request(
        self, request_id: int, *, account_id: int, encoded_password: str
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_FRIEND_REQUEST.format(request_id))}

        route = Route(
            POST,
            GET_FRIEND_REQUEST,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            request_id=request_id,
            account_id=account_id,
            gjp=encoded_password,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

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

        route = Route(
            POST,
            GET_FRIEND_REQUESTS,
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

        if type is FriendRequestType.OUTGOING:
            route.update(get_sent=1, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def like_item(
        self,
        type: LikeType,
        item_id: int,
        special_id: int,
        dislike: bool = False,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(FAILED_TO_LIKE_ITEM.format(item_id))}

        like = not dislike

        udid = self.generate_udid()
        uuid = self.generate_uuid()

        random_string = generate_random_string()

        values = (special_id, item_id, int(like), type.value, random_string, account_id, udid, uuid)

        check = generate_check(map(str, values), Key.LIKE_RATE, Salt.LIKE_RATE)

        route = Route(
            POST,
            LIKE_ITEM,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            item_id=item_id,
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

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def like_user_comment(
        self,
        comment_id: int,
        dislike: bool = False,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        return await self.like_item(
            LikeType.USER_COMMENT,
            comment_id,
            comment_id,
            dislike=dislike,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def like_level_comment(
        self,
        comment_id: int,
        level_id: int,
        dislike: bool = False,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        return await self.like_item(
            LikeType.LEVEL_COMMENT,
            comment_id,
            level_id,
            dislike=dislike,
            account_id=account_id,
            encoded_password=encoded_password,
        )

    async def like_level(
        self,
        level_id: int,
        dislike: bool = False,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        return await self.like_item(
            LikeType.LEVEL,
            level_id,
            0,
            dislike=dislike,
            account_id=account_id,
            encoded_password=encoded_password,
        )

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
        percentage = 0

        type = CommentType.USER

        values = (account_name, content, level_id, percentage, type.value)

        check = generate_check(map(str, values), Key.COMMENT, Salt.COMMENT)

        route = Route(
            POST,
            POST_USER_COMMENT,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            comment=content,
            level_id=level_id,
            c_type=type.value,
            percent=percentage,
            account_id=account_id,
            user_name=account_name,
            gjp=encoded_password,
            chk=check,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        if CommentBannedModel.can_be_in(response):
            ban = CommentBannedModel.from_robtop(response)

            raise CommentBanned(timeout=ban.timeout, reason=ban.reason)

        return int_or(response, 0)

    async def post_level_comment(
        self,
        level_id: int,
        percentage: int,
        content: Optional[str] = None,
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

        values = (account_name, content, level_id, percentage, type.value)

        check = generate_check(map(str, values), Key.COMMENT, Salt.COMMENT)

        route = Route(
            POST,
            POST_USER_COMMENT,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            comment=content,
            level_id=level_id,
            c_type=type.value,
            percent=percentage,
            account_id=account_id,
            user_name=account_name,
            gjp=encoded_password,
            chk=check,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

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

        route = Route(
            POST,
            DELETE_USER_COMMENT,
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

        response = await self.request_route(route, error_codes=error_codes)

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

        route = Route(
            POST,
            DELETE_LEVEL_COMMENT,
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

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(response, 0)

    async def get_user_comments_on_page(
        self,
        user_id: int,
        page: int = DEFAULT_PAGE,
        *,
        strategy: CommentStrategy,
    ) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_USER_LEVEL_COMMENTS.format(user_id))}

        route = Route(
            POST,
            GET_USER_COMMENTS,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            total=0,
            mode=strategy.value,
            user_id=user_id,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

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

        if count < 0:
            count += COMMENT_ADD

        route = Route(
            POST,
            GET_LEVEL_COMMENTS,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            page=page,
            total=0,
            count=count,
            mode=strategy.value,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def get_gauntlets(self) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_GAUNTLETS)}

        route = Route(
            POST,
            GET_GAUNTLETS,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def get_map_packs_on_page(self, page: int = DEFAULT_PAGE) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_MAP_PACKS)}

        route = Route(
            POST,
            GET_MAP_PACKS,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def get_quests(self, account_id: int, encoded_password: str) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_QUESTS)}

        udid = self.generate_udid()
        uuid = self.generate_uuid()

        check = generate_random_string_and_encode_value(key=Key.QUESTS)

        route = Route(
            POST,
            GET_QUESTS,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            account_id=account_id,
            gjp=encoded_password,
            udid=udid,
            uuid=uuid,
            chk=check,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

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

        udid = self.generate_udid()
        uuid = self.generate_uuid()

        chk = generate_random_string_and_encode_value(key=Key.CHESTS)

        route = Route(
            POST,
            GET_CHESTS,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            reward_type=reward_type.value,
            account_id=account_id,
            gjp=encoded_password,
            udid=udid,
            uuid=uuid,
            chk=chk,
            r1=chest_1_count,
            r2=chest_2_count,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def get_featured_artists_on_page(self, page: int = DEFAULT_PAGE) -> str:
        error_codes = {-1: MissingAccess(FAILED_TO_GET_FEATURED_ARTISTS)}

        total = 0

        route = Route(
            POST,
            GET_FEATURED_ARTISTS,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            total=total,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def get_song(self, song_id: int) -> str:
        error_codes = {
            -1: MissingAccess(FAILED_TO_GET_SONG.format(song_id)),
            -2: SongRestricted(song_id),
        }

        route = Route(
            POST,
            GET_SONG,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            song_id=song_id,
            secret=Secret.MAIN.value,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return response

    async def get_newgrounds_song(self, song_id: int) -> str:
        response = await self.request(GET, NEWGROUNDS_SONG_LISTEN.format(song_id))

        return response.replace(BACKSLASH, EMPTY)

    async def search_newgrounds_songs_on_page(self, query: str, page: int = DEFAULT_PAGE) -> str:
        page += 1  # 1-based indexing

        response = await self.request(
            GET,
            NEWGROUNDS_SEARCH.format(AUDIO),
            params=dict(terms=query, page=page + 1),
        )

        return response

    async def search_newgrounds_users_on_page(self, query: str, page: int = DEFAULT_PAGE) -> str:
        page += 1  # 1-based indexing

        response = await self.request(
            GET,
            NEWGROUNDS_SEARCH.format(USERS),
            params=dict(terms=query, page=page),
        )

        return response

    async def get_newgrounds_user_songs_on_page(
        self, name: str, page: int = DEFAULT_PAGE
    ) -> Mapping[str, Any]:
        page += 1  # 1-based indexing

        response = await self.request(
            GET,
            NEWGROUNDS_SONG_PAGE.format(name, page),
            type=ResponseType.JSON,
            headers={REQUESTED_WITH: XML_HTTP_REQUEST},
        )

        return response


RequestHook = MaybeAsyncUnary[HTTPClient, None]

E = TypeVar("E", bound=AnyException)


@frozen()
class HTTPClientContextManager(Generic[C]):
    client: C = field()
    attributes: Namespace = field(repr=False)
    saved_attributes: Namespace = field(factory=dict, repr=False, init=False)

    def __init__(self, client: C, **attributes: Any) -> None:
        self.__attrs_init__(client, attributes)

    def apply(self) -> None:
        client = self.client
        attributes = self.attributes
        saved_attributes = self.saved_attributes

        for attribute, value in attributes.items():
            saved_attributes[attribute] = get_attribute(client, attribute, None)
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
