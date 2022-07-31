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
    Any, AnyStr, BinaryIO, ClassVar, Generic, Mapping, Optional, Set, Type, TypeVar, Union, overload
)
from uuid import uuid4 as generate_uuid

from aiohttp import BasicAuth, ClientError, ClientSession, ClientTimeout
from attrs import define, field, frozen
from tqdm import tqdm as progess  # type: ignore
from typing_extensions import Literal
from yarl import URL

from gd.api.recording import Recording
from gd.async_utils import maybe_await_call, shutdown_loop
from gd.constants import DEFAULT_SPECIAL, EMPTY
from gd.encoding import encode_base64_string_url_safe, generate_check, generate_random_string
from gd.versions import CURRENT_BINARY_VERSION, CURRENT_GAME_VERSION, GameVersion, Version
from gd.typing import AnyException, DynamicTuple, Headers, IntString, IntoPath, JSONType, MaybeAsyncUnary, MaybeIterable, Namespace, Parameters, URLString, is_bytes, is_iterable, is_string
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
from gd.models import CommentBannedModel
from gd.models_utils import concat_extra_string
from gd.string_utils import concat_comma, password_str, tick
from gd.text_utils import snake_to_camel
from gd.timer import create_timer
from gd.version import python_version_info, version_info

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
XML_HTTP_REQUEST = "XML" + "HTTP".title() + "Request"

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
REMOVE_FRIEND = "removeGJFriend20.php"
SEND_MESSAGE = "uploadGJMessage20.php"
GET_MESSAGE = "downloadGJMessage20.php"
DELETE_MESSAGE = "deleteGJMessages20.php"
GET_MESSAGES = "getGJMessages20.php"
SEND_FRIEND_REQUEST = "uploadFriendRequest20.php"
DELETE_FRIEND_REQUEST = "deleteGJFriendRequests20.php"
ACCEPT_FRIEND_REQUEST = "acceptGJFriendRequest20.php"
GET_FRIEND_REQUEST = "readGJFriendRequest20.php"
GET_FRIEND_REQUESTS = "getGJFriendRequests20.php"
LIKE_COMMENT = LIKE_LEVEL = "likeGJItem211.php"
COMMENT_LEVEL = "uploadGJComment21.php"
POST_COMMENT = "uploadGJAccComment20.php"
DELETE_LEVEL_COMMENT = "deleteGJComment20.php"
DELETE_COMMENT = "deleteGJAccComment20.php"
GET_USER_LEVEL_COMMENTS = "getGJCommentHistory.php"
GET_USER_COMMENTS = "getGJAccountComments20.php"
GET_LEVEL_COMMENTS = "getGJComments21.php"
GET_GAUNTLETS = "getGJGauntlets21.php"
GET_MAP_PACKS = "getGJMapPacks21.php"
GET_QUESTS = "getGJChallenges.php"
GET_CHESTS = "getGJRewards.php"
GET_TOP_AUTHORS = "getGJTopArtists.php"
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

AUDIO = "audio"
USERS = "users"
LEVELS = "levels"


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
            url=url / route.route,
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

    async def search_users_on_page(self, query: Union[int, str], page: int = 0) -> str:
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
        amount: int = 100,
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
            count=amount,
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
        page: int = 0,
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
            query = concat_comma(query)

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
        name: str = "Unnamed",
        id: int = 0,
        version: int = 1,
        length: LevelLength = LevelLength.TINY,  # type: ignore
        track_id: int = 0,
        description: str = "",
        song_id: int = 0,
        is_auto: bool = False,
        original: int = 0,
        two_player: bool = False,
        objects: int = 0,
        coins: int = 0,
        stars: int = 0,
        unlisted: bool = False,
        friends_only: bool = False,
        low_detail_mode: bool = False,
        password: Optional[Union[int, str]] = None,
        copyable: bool = False,
        recording: Iterable[RecordingEntry] = (),
        editor_seconds: int = 0,
        copies_seconds: int = 0,
        data: str = "",
        *,
        account_id: int,
        account_name: str,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess("Failed to upload level.")}

        if is_level_probably_decoded(data):
            if not objects:
                objects = object_count(data)

            data = zip_level_str(data)

        extra_string = self.generate_extra_string()

        description = encode_base64_str(description)

        level_seed = generate_level_seed(data)

        seed = generate_rs()
        other_seed = generate_chk(
            values=[level_seed], key=Key.LEVEL, salt=Salt.LEVEL  # type: ignore
        )

        level_password = Password(password, copyable)

        just_unlisted = 0
        listed_for_friends = 0

        if friends_only:
            just_unlisted = 1
            listed_for_friends = 1

        elif unlisted:
            just_unlisted = 1

        recording_str = zip_level_str(Recording.collect_string(recording))

        route = Route(
            POST,
            "/uploadGJLevel21.php",
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
            auto=int(is_auto),
            original=original,
            two_player=int(two_player),
            objects=objects,
            coins=coins,
            requested_stars=stars,
            unlisted=just_unlisted,
            unlisted2=listed_for_friends,
            ldm=int(low_detail_mode),
            password=level_password.to_robtop_number(),
            level_string=data,
            extra_string=extra_string,
            level_info=recording_str,
            seed=seed,
            seed2=other_seed,
            wt=editor_seconds,
            wt2=copies_seconds,
            account_id=account_id,
            user_name=account_name,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def rate_level(
        self, level_id: int, stars: int, *, account_id: int, encoded_password: str
    ) -> int:
        error_codes = {-1: MissingAccess(f"Failed to rate level by ID: {level_id}.")}
        udid = self.generate_udid()
        uuid = self.generate_uuid()
        rs = generate_rs()

        chk = generate_chk(
            values=[level_id, stars, rs, account_id, udid, uuid],
            key=Key.LIKE_RATE,  # type: ignore
            salt=Salt.LIKE_RATE,  # type: ignore
        )

        route = Route(
            POST,
            "/rateGJStars211.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            stars=stars,
            udid=udid,
            uuid=uuid,
            rs=rs,
            chk=chk,
            account_id=account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

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
            -1: MissingAccess(f"Failed to demon-rate level by ID: {level_id}."),
            -2: MissingAccess(
                f"Missing moderator permissions to demon-rate level by ID: {level_id}."
            ),
        }

        route = Route(
            POST,
            "/rateGJDemon21.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            rating=rating.value,
            mode=int(as_mod),
            account_id=account_id,
            gjp=encoded_password,
            secret=self.get_secret("mod"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def send_level(
        self,
        level_id: int,
        stars: int,
        feature: bool,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(f"Failed to send a level by ID: {level_id}."),
            -2: MissingAccess(f"Missing moderator permissions to send level by ID: {level_id}."),
        }

        route = Route(
            POST,
            "/suggestGJStars20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            stars=stars,
            feature=int(feature),
            account_id=account_id,
            gjp=encoded_password,
            secret=self.get_secret("mod"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def get_level_top(
        self,
        level_id: int,
        strategy: LevelLeaderboardStrategy,
        *,
        account_id: int,
        encoded_password: str,
    ) -> str:
        # timely_type: TimelyType = TimelyType.NOT_TIMELY,
        # timely_id: int = 0,
        # played: bool = False,
        # percent: int = 0,
        # jumps: int = 0,
        # attempts: int = 0,
        # seconds: int = 0,
        # coins: int = 0,

        error_codes = {
            -1: MissingAccess(f"Failed to get leaderboard of the level by ID: {level_id}.")
        }

        # seed = generate_leaderboard_seed(jumps, percentage, seconds, played)

        # if timely_type is TimelyType.WEEKLY:
        #     timely_id += 100_000

        # chk = generate_chk(
        #     values=[
        #         account_id,
        #         level_id,
        #         percentage,
        #         seconds,
        #         jumps,
        #         attempts,
        #         percent,
        #         100 - percent,
        #         1,
        #         coins,
        #         timely_id,
        #         rs,
        #     ],
        #     key=Key.LEVEL_LEADERBOARD,  # type: ignore
        #     salt=Salt.LEVEL_LEADERBOARD,  # type: ignore
        # )

        route = Route(
            POST,
            "/getGJLevelScores211.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            account_id=account_id,
            gjp=encoded_password,
            type=strategy.value,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        # route.update(
        #     percent=percent,
        #     s1=attempts + 8354,
        #     s2=jumps + 3991,
        #     s3=seconds + 4085,
        #     s4=seed,
        #     s5=random.randint(100, 10_000),  # not sure about this one
        #     s6="",  # this is progress string, we will add that later
        #     s7=rs,
        #     s8=attempts,
        #     s9=coins + 5819,
        #     s10=timely_id,
        #     chk=chk,
        # )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def block_or_unblock(
        self,
        account_id: int,
        unblock: bool,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        if unblock:
            endpoint = "/unblockGJUser20.php"
            string = "unblock"

        else:
            endpoint = "/blockGJUser20.php"
            string = "block"

        error_codes = {
            -1: MissingAccess(f"Failed to {string} the user by Account ID: {account_id}.")
        }

        route = Route(
            POST,
            endpoint,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def unfriend_user(
        self, account_id: int, *, client_account_id: int, encoded_password: str
    ) -> int:
        error_codes = {
            -1: MissingAccess(f"Failed to unfriend the user by account ID: {account_id}.")
        }

        route = Route(
            POST,
            "/removeGJFriend20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def send_message(
        self,
        account_id: int,
        subject: Optional[str] = None,
        content: Optional[str] = None,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(f"Failed to send a message to the user by account ID: {account_id}.")
        }

        if subject is None:
            subject = ""

        if content is None:
            content = ""

        route = Route(
            POST,
            "/uploadGJMessage20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            subject=encode_base64_str(subject),
            body=encode_robtop_str(content, Key.MESSAGE),  # type: ignore
            to_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def download_message(
        self,
        message_id: int,
        type: MessageType,
        *,
        account_id: int,
        encoded_password: str,
    ) -> str:
        error_codes = {-1: MissingAccess(f"Failed to read a message by ID: {message_id}.")}

        route = Route(
            POST,
            "/downloadGJMessage20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            account_id=account_id,
            message_id=message_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        if type is MessageType.OUTGOING:
            route.update(is_sender=1, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def delete_message(
        self,
        message_id: int,
        type: MessageType,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(f"Failed to delete a message by ID: {message_id}.")}

        route = Route(
            POST,
            "/deleteGJMessages20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            account_id=account_id,
            message_id=message_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        if type is MessageType.OUTGOING:
            route.update(is_sender=1, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def get_messages_on_page(
        self, type: MessageType, page: int, *, account_id: int, encoded_password: str
    ) -> str:
        error_codes = {
            -1: MissingAccess(f"Failed to get messages on page {page}."),
            -2: NothingFound("Message"),
        }

        route = Route(
            POST,
            "/getGJMessages20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            total=0,
            account_id=account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        if type is MessageType.OUTGOING:
            route.update(get_sent=1, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def send_friend_request(
        self,
        account_id: int,
        message: Optional[str] = None,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(f"Failed to send a friend request to the user by ID: {account_id}.")
        }

        if message is None:
            message = ""

        route = Route(
            POST,
            "/uploadFriendRequest20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            comment=encode_base64_str(message),
            to_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        if not response:
            return 1

        return int_or(cast(str, response), 0)

    async def delete_friend_request(
        self,
        account_id: int,
        type: FriendRequestType,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(
                f"Failed to delete a friend request of the user with ID: {account_id}."
            )
        }

        route = Route(
            POST,
            "/deleteGJFriendRequests20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        if type is FriendRequestType.OUTGOING:
            route.update(is_sender=1, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def accept_friend_request(
        self,
        account_id: int,
        request_id: int,
        type: FriendRequestType,
        *,
        client_account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(
                f"Failed to accept a friend request of the user with ID: {account_id}."
            )
        }

        route = Route(
            POST,
            "/acceptGJFriendRequest20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            request_id=request_id,
            account_id=client_account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        if type is FriendRequestType.OUTGOING:
            route.update(is_sender=1, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def read_friend_request(
        self, request_id: int, *, account_id: int, encoded_password: str
    ) -> int:
        error_codes = {-1: MissingAccess(f"Failed to read a friend request with ID: {request_id}.")}

        route = Route(
            POST,
            "/readGJFriendRequest20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            request_id=request_id,
            account_id=account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def get_friend_requests_on_page(
        self,
        type: FriendRequestType,
        page: int,
        *,
        account_id: int,
        encoded_password: str,
    ) -> str:
        error_codes = {
            -1: MissingAccess(f"Failed to get friend requests on page {page}."),
            -2: NothingFound("FriendRequest"),
        }

        route = Route(
            POST,
            "/getGJFriendRequests20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            total=0,
            account_id=account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        if type is FriendRequestType.OUTGOING:
            route.update(get_sent=1, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def like_or_dislike(
        self,
        type: LikeType,
        item_id: int,
        special_id: int,
        dislike: bool = False,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(f"Failed to like an item by ID: {item_id} (special {special_id}).")
        }

        type_id = type.value

        like = not dislike

        udid = self.generate_udid()
        uuid = self.generate_uuid()
        rs = generate_rs()

        int_like = int(like)

        chk = generate_chk(
            values=[special_id, item_id, int_like, type_id, rs, account_id, udid, uuid],
            key=Key.LIKE_RATE,  # type: ignore
            salt=Salt.LIKE_RATE,  # type: ignore
        )

        route = Route(
            POST,
            "/likeGJItem211.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            item_id=item_id,
            type=type_id,
            special=special_id,
            like=int_like,
            account_id=account_id,
            gjp=encoded_password,
            udid=udid,
            uuid=uuid,
            rs=rs,
            chk=chk,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def post_comment(
        self,
        type: CommentType,
        content: Optional[str] = None,
        level_id: int = 0,
        percent: int = 0,
        *,
        account_id: int,
        account_name: str,
        encoded_password: str,
    ) -> int:  # XXX: We might want to use two separate functions in case of API update.
        type_name = type.name.casefold()

        error_codes = {
            -1: MissingAccess(f"Failed to post a {type_name} comment."),
            -10: CommentBanned(timeout=None),
        }

        if content is None:
            content = ""

        content = encode_base64_str(content)

        chk = generate_chk(
            values=[account_name, content, level_id, percent, type.value],
            key=Key.COMMENT,  # type: ignore
            salt=Salt.COMMENT,  # type: ignore
        )

        if type is CommentType.LEVEL:
            endpoint = "/uploadGJComment21.php"

        else:
            endpoint = "/uploadGJAccComment20.php"

        route = Route(
            POST,
            endpoint,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            comment=content,
            level_id=level_id,
            c_type=type.value,
            percent=percent,
            account_id=account_id,
            user_name=account_name,
            gjp=encoded_password,
            chk=chk,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = cast(str, await self.request_route(route, error_codes=error_codes))

        if CommentBannedModel.maybe_in(response):
            ban = CommentBannedModel.from_string(response)

            raise CommentBanned(timeout=ban.timeout, reason=ban.reason)

        return int_or(response, 0)

    async def delete_comment(
        self,
        comment_id: int,
        type: CommentType,
        level_id: int = 0,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess(f"Failed to delete a comment by ID: {comment_id}.")}

        if type is CommentType.LEVEL:
            endpoint = "/deleteGJComment20.php"

        else:
            endpoint = "/deleteGJAccComment20.php"

        route = Route(
            POST,
            endpoint,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            comment_id=comment_id,
            c_type=type.value,
            level_id=level_id,
            account_id=account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def get_user_comments_on_page(
        self,
        account_id: int,
        user_id: int,
        type: CommentType,
        page: int = 0,
        *,
        strategy: CommentStrategy,
    ) -> str:
        error_codes = {
            -1: MissingAccess(f"Failed to get comment for user by Account ID: {account_id}.")
        }

        if type is CommentType.LEVEL:
            endpoint = "/getGJCommentHistory.php"

        else:
            endpoint = "/getGJAccountComments20.php"

        route = Route(
            POST,
            endpoint,
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            total=0,
            mode=strategy.value,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        if type is CommentType.LEVEL:
            route.update(user_id=user_id, to_camel=True)

        else:
            route.update(account_id=account_id, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def get_level_comments_on_page(
        self,
        level_id: int,
        amount: int,
        page: int = 0,
        *,
        strategy: CommentStrategy,
    ) -> str:
        error_codes = {
            -1: MissingAccess(f"Failed to get comments of a level by ID: {level_id}."),
            -2: NothingFound("Comment"),
        }

        if amount < 0:
            amount += COMMENT_TO_ADD

        route = Route(
            POST,
            "/getGJComments21.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            page=page,
            total=0,
            count=amount,
            mode=strategy.value,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def get_gauntlets(self) -> str:
        error_codes = {-1: MissingAccess("Failed to get gauntlets.")}

        route = Route(
            POST,
            "/getGJGauntlets21.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def get_map_packs_on_page(self, page: int = 0) -> str:
        error_codes = {-1: MissingAccess("Failed to get map packs.")}

        route = Route(
            POST,
            "/getGJMapPacks21.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def get_quests(self, account_id: int, encoded_password: str) -> str:
        error_codes = {-1: MissingAccess("Failed to get quests.")}

        udid = self.generate_udid()
        uuid = self.generate_uuid()

        chk = generate_rs_and_encode_number(length=5, key=Key.QUESTS)  # type: ignore

        route = Route(
            POST,
            "/getGJChallenges.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            account_id=account_id,
            gjp=encoded_password,
            udid=udid,
            uuid=uuid,
            chk=chk,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def get_chests(
        self,
        reward_type: RewardType,
        chest_1_count: int = 0,
        chest_2_count: int = 0,
        *,
        account_id: int,
        encoded_password: str,
    ) -> str:
        error_codes = {-1: MissingAccess("Failed to get chests.")}

        udid = self.generate_udid()
        uuid = self.generate_uuid()

        chk = generate_rs_and_encode_number(length=5, key=Key.CHESTS)  # type: ignore

        route = Route(
            POST,
            "/getGJRewards.php",
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
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def get_featured_artists_on_page(self, page: int = 0) -> str:
        error_codes = {-1: MissingAccess("Failed to get featured artists.")}

        route = Route(
            POST,
            "/getGJTopArtists.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            page=page,
            total=0,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def get_song(self, song_id: int) -> str:
        error_codes = {
            -1: MissingAccess(f"Can not get song by ID: {song_id}."),
            -2: SongRestricted(song_id),
        }

        route = Route(
            POST,
            "/getGJSongInfo.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            song_id=song_id,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def get_newgrounds_song(self, song_id: int) -> str:
        response = await self.request(GET, NEWGROUNDS_SONG_LISTEN.format(id=song_id))
        return cast(str, response).replace("\\", "")

    async def get_artist_info(self, song_id: int) -> str:
        error_codes = {-1: MissingAccess(f"Failed to fetch artist info for ID: {song_id}")}

        route = Route(
            GET,
            "/testSong.php",
            song_id=song_id,
            are_params=True,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def search_newgrounds_songs_on_page(self, query: str, page: int = 0) -> str:
        response = await self.request(
            GET,
            NEWGROUNDS_SEARCH.format(type="audio"),
            params=dict(terms=query, page=page + 1),
        )

        return cast(str, response)

    async def search_newgrounds_users_on_page(self, query: str, page: int = 0) -> str:
        response = await self.request(
            GET,
            NEWGROUNDS_SEARCH.format(type="users"),
            params=dict(terms=query, page=page + 1),
        )

        return cast(str, response)

    async def get_newgrounds_user_songs_on_page(
        self, name: str, page: int = 0
    ) -> Mapping[str, Any]:
        response = await self.request(
            GET,
            NEWGROUNDS_SONG_PAGE.format(name=name, page=page + 1),
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
