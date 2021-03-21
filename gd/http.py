import asyncio
import atexit
import random
import time
import types
import uuid

from pathlib import Path

import aiohttp
import tqdm  # type: ignore
from yarl import URL

from gd.api.recording import Recording, RecordingEntry
from gd.async_utils import get_running_loop, maybe_coroutine, shutdown_loop
from gd.converters import GameVersion, Password, Version
from gd.crypto import (  # generate_leaderboard_seed,
    Key,
    Salt,
    encode_base64_str,
    encode_robtop_str,
    generate_chk,
    generate_level_seed,
    generate_rs,
    generate_rs_and_encode_number,
    zip_level_str,
)
from gd.decorators import synchronize
from gd.enums import (
    AccountURLType,
    CommentState,
    CommentStrategy,
    CommentType,
    DemonDifficulty,
    FriendRequestState,
    FriendRequestType,
    IconType,
    LeaderboardStrategy,
    LevelLeaderboardStrategy,
    LevelLength,
    LikeType,
    MessageState,
    MessageType,
    RewardType,
    SearchStrategy,
    Secret,
    SimpleRelationshipType,
)
from gd.errors import (
    CommentBanned,
    HTTPError,
    HTTPStatusError,
    LoginFailure,
    LoginRequired,
    MissingAccess,
    NothingFound,
    SongRestricted,
)
from gd.filters import Filters
from gd.logging import get_logger
from gd.model import CommentBannedModel  # type: ignore
from gd.text_utils import is_level_probably_decoded, make_repr, object_count, snake_to_camel
from gd.typing import (
    JSON,
    Any,
    Awaitable,
    Callable,
    Dict,
    IO,
    Iterable,
    Mapping,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    cast,
)
from gd.version import python_version_info, version_info

__all__ = ("Route", "HTTPClient")

log = get_logger(__name__)

DATABASE = "database"
ROOT = "/"

BASE = "http://www.boomlings.com/database"
GD_BASE = "http://geometrydash.com/database"

NEWGROUNDS_SONG_LISTEN = "https://www.newgrounds.com/audio/listen/{song_id}"
NEWGROUNDS_SONG_PAGE = "https://{name}.newgrounds.com/audio/page/{page}"
NEWGROUNDS_SEARCH = "https://www.newgrounds.com/search/conduct/{type}"

# I might sound stupid but I really like "XMLHTTPRequest", and so I wrote this ~ nekit
XML_HTTP_REQUEST = "XML" + "HTTP".title() + "Request"

CLIENTS: Set["HTTPClient"] = set()

VALID_ERRORS = (OSError, aiohttp.ClientError)

HEAD = "HEAD"
GET = "GET"

POST = "POST"
PUT = "PUT"
PATCH = "PATCH"

DELETE = "DELETE"

CONNECT = "CONNECT"
OPTIONS = "OPTIONS"
TRACE = "TRACE"

CHUNK_SIZE = 64 * 1024

T = TypeVar("T")

RequestHook = Callable[["HTTPClient"], Union[T, Awaitable[T]]]
ResponseData = Union[bytes, str, JSON]

COMMENT_TO_ADD = 1 << 31


async def read_data(
    response: aiohttp.ClientResponse,
    raw: bool = False,
    json: bool = False,
    encoding: str = "utf-8",
) -> ResponseData:
    if raw:
        return await response.read()

    elif json:
        return await response.json(encoding=encoding, content_type=None)

    else:
        return await response.text(encoding=encoding)


def is_error_code(data: Union[bytes, str]) -> bool:
    if isinstance(data, bytes):
        return bool(data) and data[0] == b"-" and data[1:].isdigit()

    else:
        return bool(data) and data[0] == "-" and data[1:].isdigit()


def int_or(data: Union[bytes, str], default: int = 0) -> int:
    try:
        return int(data)

    except ValueError:
        return default


def unexpected_error_code(error_code: int) -> MissingAccess:
    return MissingAccess(f"Got unexpected error code: {error_code}.")


def snake_to_camel_with_id(string: str) -> str:
    return snake_to_camel(string).replace("Id", "ID")


class Route:
    def __init__(
        self,
        method: str,
        path: str,
        *,
        to_camel: bool = False,
        are_params: bool = False,
        **parameters,
    ) -> None:
        self.method = method
        self.path = path.strip("/")
        self.are_params = are_params

        self.parameters: Dict[str, Any] = {}

        self.update(parameters, to_camel=to_camel)

    def update(
        self, mapping: Mapping[str, Any] = None, *, to_camel: bool = False, **parameters,
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
        return f"{self.method} {self.path}"

    def __repr__(self) -> str:
        info = {"method": self.method, "path": self.path, "parameters": self.parameters}

        return make_repr(self, info)


async def close_all_clients() -> None:
    for client in CLIENTS:
        await client.close()

    CLIENTS.clear()


def close_all_clients_sync() -> None:
    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    loop.run_until_complete(close_all_clients())

    shutdown_loop(loop)


atexit.register(close_all_clients_sync)


@synchronize
class HTTPClient:
    USER_AGENT = f"python/{python_version_info} gd.py/{version_info}"
    REQUEST_LOG = "{method} {url} has returned {status}"
    SUCCESS_LOG = "{method} {url} has received {data}"

    DEFAULT_SKIP_HEADERS = ["Accept-Encoding", "User-Agent"]

    def __init__(
        self,
        *,
        url: Union[str, URL] = BASE,
        proxy: Optional[str] = None,
        proxy_auth: Optional[aiohttp.BasicAuth] = None,
        timeout: Union[float, int] = 150,
        game_version: GameVersion = GameVersion(2, 1),
        binary_version: Version = Version(3, 5),
        gd_world: bool = False,
        forwarded_for: Optional[str] = None,
        use_user_agent: bool = False,
    ) -> None:
        self.session: Optional[aiohttp.ClientSession] = None

        self.set_url(url)

        self.proxy = proxy
        self.proxy_auth = proxy_auth

        self.timeout = timeout

        self.game_version = game_version
        self.binary_version = binary_version
        self.gd_world = gd_world

        self.forwarded_for = forwarded_for
        self.use_user_agent = use_user_agent

        self._before_request: Optional[RequestHook] = None
        self._after_request: Optional[RequestHook] = None

        CLIENTS.add(self)

    def __repr__(self) -> str:
        info = {
            "url": self.str_url,
            "timeout": self.timeout,
            "game_version": self.game_version,
            "binary_version": self.binary_version,
            "gd_world": self.gd_world,
        }
        return make_repr(self, info)

    def change(self, **attrs) -> "HTTPClientContextManager":
        return HTTPClientContextManager(self, **attrs)

    def get_url(self) -> URL:
        return URL(self.str_url)

    def set_url(self, url: Union[str, URL]) -> None:
        self.str_url = str(url)

    url = property(get_url, set_url)

    def create_timeout(self) -> aiohttp.ClientTimeout:
        return aiohttp.ClientTimeout(total=self.timeout)

    def before_request(self, request_hook: RequestHook) -> RequestHook:
        self._before_request = request_hook

        return request_hook

    def after_request(self, request_hook: RequestHook) -> RequestHook:
        self._after_request = request_hook

        return request_hook

    async def call_before_request_hook(self) -> Optional[T]:
        if self._before_request:
            return await maybe_coroutine(self._before_request, self)

        return None

    async def call_after_request_hook(self) -> Optional[T]:
        if self._after_request:
            return await maybe_coroutine(self._after_request, self)

        return None

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()

            self.session = None

    async def create_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(skip_auto_headers=self.DEFAULT_SKIP_HEADERS)

    async def ensure_session(self) -> None:
        if self.session is None:
            self.session = await self.create_session()

        loop = get_running_loop()

        maybe_loop = getattr(self.session, "_loop", None)  # XXX: keep up with aiohttp's internals

        if maybe_loop is not None and maybe_loop is not loop:
            await self.close()

            self.session = await self.create_session()

    async def download(
        self,
        url: Union[URL, str],
        method: str = GET,
        chunk_size: int = CHUNK_SIZE,
        with_bar: bool = False,
        close: bool = False,
        file: Optional[Union[str, Path, IO]] = None,
        **kwargs,
    ) -> Optional[bytes]:
        r"""Download the file at ``url`` with ``method``.

        Parameters
        ----------
        method: :class:`str`
            HTTP method to send request with. Default is ``GET``.

        url: Union[:class:`~yarl.URL`, :class:`str`]
            URL to request file from.

        chunk_size: :class:`int`
            Amount of data to read for one chunk. ``-1`` to read until EOF.

        with_bar: :class:`bool`
            Whether to show progress bar when downloading. ``False`` by default.

        close: :class:`bool`
            Whether to close the underlying ``file`` after finishing.

        file: Optional[Union[:class:`str`, :class:`~pathlib.Path`, IO]]
            File to write downloaded data to. If not given,
            this function returns all the data as the result.

        \*\*kwargs
            Keywoard arguments to pass to :meth:`aiohttp.ClientSession.request`.

        Returns
        -------
        Optional[:class:`bytes`]
            Data downloaded, if ``file`` is not given or ``None``. Otherwise, returns ``None``.
        """
        if isinstance(file, (str, Path)):
            file = open(file, "wb")
            close = True

        await self.ensure_session()

        async with self.session.request(  # type: ignore
            url=url, method=method, **kwargs
        ) as response:
            if file is None:
                result = bytes()

            if with_bar:
                bar = tqdm.tqdm(total=response.content_length, unit="b", unit_scale=True)

            while True:
                chunk = await response.content.read(chunk_size)

                if not chunk:
                    break

                if file is None:
                    result += chunk

                else:
                    file.write(chunk)

                if with_bar:
                    bar.update(len(chunk))

            if with_bar:
                bar.close()

        if close and file:
            file.close()

        if file is None:
            return result

        return None

    async def request_route(
        self,
        route: Route,
        raw: bool = False,
        json: bool = False,
        error_codes: Optional[Mapping[int, BaseException]] = None,
        headers: Optional[Dict[str, Any]] = None,
        base_url: Optional[Union[str, URL]] = None,
        retries: int = 2,
    ) -> Optional[ResponseData]:
        url = URL(self.url if base_url is None else base_url)

        args = dict(
            method=route.method, url=url / route.path, raw=raw, json=json, error_codes=error_codes,
        )

        args["params" if route.are_params else "data"] = route.parameters

        return await self.request(**args)  # type: ignore

    async def request(
        self,
        method: str,
        url: Union[str, URL],
        data: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
        raw: bool = False,
        json: bool = False,
        read: bool = True,
        error_codes: Optional[Mapping[int, BaseException]] = None,
        headers: Optional[Dict[str, Any]] = None,
        retries: int = 2,
    ) -> Optional[ResponseData]:
        await self.ensure_session()

        await self.call_before_request_hook()

        if retries < 0:
            attempt_left = -1

        elif retries == 0:
            attempt_left = 1

        else:
            attempt_left = retries + 1

        if headers is None:
            headers = {}

        if self.use_user_agent:
            headers.setdefault("User-Agent", self.USER_AGENT)

        if self.forwarded_for:
            headers.setdefault("X-Forwarded-For", self.forwarded_for)

        lock = asyncio.Lock()
        error: Optional[BaseException] = None

        while attempt_left:
            try:
                async with lock, self.session.request(  # type: ignore
                    url=url,
                    method=method,
                    data=data,
                    params=params,
                    proxy=self.proxy,
                    proxy_auth=self.proxy_auth,
                    headers=headers,
                    timeout=self.create_timeout(),
                ) as response:

                    log.debug("%s %s has returned %d", method, url, response.status)

                    if not read:
                        return None

                    response_data = await read_data(response, raw=raw, json=json)

                    if 200 <= response.status < 300:  # successful

                        log.debug("%s %s has received %s", method, url, response_data)

                        if isinstance(response_data, (bytes, str)):

                            if error_codes and is_error_code(response_data):
                                error_code = int(response_data)

                                raise error_codes.get(error_code, unexpected_error_code(error_code))

                        return response_data

                    if response.status >= 400:
                        error = HTTPStatusError(response.status, response.reason)

            except VALID_ERRORS as valid_error:
                error = HTTPError(valid_error)

            finally:
                await asyncio.sleep(0)  # let underlying connections close

            attempt_left -= 1

        await self.call_after_request_hook()

        if error:
            raise error

        return None

    @staticmethod
    def generate_udid(id: Optional[int] = None, low: int = 1, high: int = 1_000_000_000) -> str:
        if id is None:
            id = random.randint(low, high)
        return f"S{id}"

    @staticmethod
    def generate_uuid() -> str:
        return f"{uuid.uuid4()}"

    @staticmethod
    def generate_extra_string(amount: int = 55) -> str:
        return "_".join(map(str, (0 for _ in range(amount))))

    def get_game_version(self) -> int:
        return self.game_version.to_robtop_number()

    def get_binary_version(self) -> int:
        return self.binary_version.to_number()

    def get_gd_world(self) -> int:
        return int(self.gd_world)

    def get_secret(self, name: str) -> str:
        return Secret.from_name(name).value

    async def ping(self, url: Union[str, URL]) -> float:
        start = time.perf_counter()

        try:
            await self.request(GET, url, read=False)

        except Exception:  # noqa
            pass

        end = time.perf_counter()

        return (end - start) * 1000

    async def login(self, name: str, password: str) -> str:
        error_codes = {
            -1: LoginFailure(name=name, password=password),
            -12: MissingAccess(f"Account {name!r} (password {password!r}) is disabled."),
        }

        route = Route(
            POST,
            "/accounts/loginGJAccount.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            user_name=name,
            password=password,
            udid=self.generate_udid(),
            secret=self.get_secret("login"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def load(self, *, account_id: int, name: str, password: str) -> str:
        error_codes = {-11: MissingAccess("Failed to load save.")}

        route = Route(
            POST,
            "/accounts/syncGJAccountNew.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            user_name=name,
            password=password,
            secret=self.get_secret("login"),
            to_camel=True,
        )

        base_url = await self.get_account_url(account_id, type=AccountURLType.LOAD)  # type: ignore

        response = await self.request_route(route, error_codes=error_codes, base_url=base_url)

        return cast(str, response)

    async def save(self, data: str, *, account_id: int, name: str, password: str) -> int:
        error_codes = {
            -1: MissingAccess("Failed to save."),
            -4: MissingAccess("Data is too large."),
            -5: MissingAccess("Invalid login credentials."),
            -6: MissingAccess("Something went wrong."),
        }

        route = Route(
            POST,
            "/accounts/backupGJAccountNew.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            save_data=data,
            user_name=name,
            password=password,
            secret=self.get_secret("login"),
            to_camel=True,
        )

        base_url = await self.get_account_url(account_id, type=AccountURLType.SAVE)  # type: ignore

        response = await self.request_route(route, error_codes=error_codes, base_url=base_url)

        return int_or(cast(str, response), 0)

    async def get_account_url(self, account_id: int, type: AccountURLType) -> URL:
        error_codes = {
            -1: MissingAccess(
                f"Failed to find {type.name.lower()} URL for Account ID: {account_id}."
            )
        }

        route = Route(
            POST,
            "/getAccountURL.php",
            account_id=account_id,
            type=type.value,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        url = URL(cast(str, response))

        if url.path == ROOT:
            return url / DATABASE

        return url

    async def get_role_id(self, account_id: int, encoded_password: str) -> int:
        error_codes = {-1: MissingAccess("No role found.")}

        route = Route(
            POST,
            "/requestUserAccess.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            account_id=account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def update_settings(
        self,
        message_state: MessageState,
        friend_request_state: FriendRequestState,
        comment_state: CommentState,
        youtube: str,
        twitter: str,
        twitch: str,
        *,
        account_id: int,
        encoded_password: str,
    ) -> int:
        error_codes = {-1: MissingAccess("Failed to update settings.")}

        route = Route(
            POST,
            "/updateGJAccSettings20.php",
            account_id=account_id,
            gjp=encoded_password,
            secret=self.get_secret("login"),
            m_s=message_state.value,
            fr_s=friend_request_state.value,
            c_s=comment_state.value,
            yt=youtube,
            twitter=twitter,
            twitch=twitch,
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def update_profile(
        self,
        stars: int,
        diamonds: int,
        coins: int,
        user_coins: int,
        demons: int,
        icon_type: IconType,
        icon: int,
        color_1_id: int,
        color_2_id: int,
        has_glow: bool,
        cube: int,
        ship: int,
        ball: int,
        ufo: int,
        wave: int,
        robot: int,
        spider: int,
        death_effect: int,
        special: int = 0,
        *,
        account_id: int,
        name: str,
        encoded_password: str,
    ) -> int:
        error_codes = {
            -1: MissingAccess(f"Failed to update profile of a user by Account ID: {account_id}.")
        }
        rs = generate_rs()

        chk = generate_chk(
            values=[
                account_id,
                user_coins,
                demons,
                stars,
                coins,
                icon_type.value,
                icon,
                diamonds,
                cube,
                ship,
                ball,
                ufo,
                wave,
                robot,
                int(has_glow),
                spider,
                death_effect,
            ],
            key=Key.USER_LEADERBOARD,  # type: ignore
            salt=Salt.USER_LEADERBOARD,  # type: ignore
        )

        route = Route(
            POST,
            "/updateGJUserScore22.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            stars=stars,
            diamonds=diamonds,
            coins=coins,
            user_coins=user_coins,
            demons=demons,
            special=special,
            icon=icon,
            icon_type=icon_type.value,
            acc_icon=cube,
            acc_ship=ship,
            acc_ball=ball,
            acc_bird=ufo,
            acc_dart=wave,
            acc_robot=robot,
            acc_spider=spider,
            acc_explosion=death_effect,
            acc_glow=int(has_glow),
            color1=color_1_id,
            color2=color_2_id,
            user_name=name,
            account_id=account_id,
            gjp=encoded_password,
            seed=rs,
            seed2=chk,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def search_users_on_page(self, query: Union[int, str], page: int = 0) -> str:
        error_codes = {-1: MissingAccess(f"Can not find results for query: {query!r}.")}

        route = Route(
            POST,
            "/getGJUsers20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            str=query,
            total=0,
            page=page,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def get_user_profile(
        self,
        account_id: int,
        *,
        client_account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> str:
        error_codes = {
            -1: MissingAccess(f"Can not find user with ID: {account_id}."),
        }

        route = Route(
            POST,
            "/getGJUserInfo20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            target_account_id=account_id,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        if client_account_id is not None and encoded_password is not None:
            route.update(account_id=client_account_id, gjp=encoded_password, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def get_relationships(
        self, type: SimpleRelationshipType, *, account_id: int, encoded_password: str
    ) -> str:
        error_codes = {
            -1: MissingAccess(f"Failed to fetch {type.name.lower()} users."),
            -2: NothingFound("AbstractUser"),
        }

        route = Route(
            POST,
            "/getGJUserList20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            type=type.value,
            account_id=account_id,
            gjp=encoded_password,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def get_top(
        self,
        strategy: LeaderboardStrategy,
        amount: int = 100,
        *,
        account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> str:
        error_codes = {
            -1: MissingAccess(f"Failed to fetch leaderboard for strategy: {strategy!r}.")
        }

        route = Route(
            POST,
            "/getGJScores20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            type=strategy.name.lower(),
            count=amount,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        if strategy.requires_login():
            if not account_id or not encoded_password:
                raise LoginRequired(f"{strategy!r} strategy requires logged in Client.")

            route.update(account_id=account_id, gjp=encoded_password, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def search_levels_on_page(
        self,
        query: Optional[Union[int, str, Iterable[Any]]] = None,
        page: int = 0,
        filters: Optional[Filters] = None,
        user_id: Optional[int] = None,
        gauntlet: Optional[int] = None,
        *,
        client_account_id: Optional[int] = None,
        client_user_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> str:
        error_codes = {-1: NothingFound("Level")}

        if filters is None:
            filters = Filters()

        if query is None:
            query = ""

        if not isinstance(query, str) and isinstance(query, Iterable):
            query = ",".join(query)

        route = Route(
            POST,
            "/getGJLevels21.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            secret=self.get_secret("main"),
            to_camel=True,
        )

        if gauntlet is not None:
            route.update(gauntlet=gauntlet)

        else:
            route.update(filters.to_parameters(), str=query, page=page, total=0, to_camel=True)

            if filters.strategy is SearchStrategy.BY_USER:
                if user_id is None:
                    if (
                        client_account_id is None
                        or client_user_id is None
                        or encoded_password is None
                    ):
                        raise MissingAccess(
                            "Can not use by-user strategy with no User ID or Client."
                        )

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
                    raise MissingAccess("Friends strategy requires logged in Client.")

                route.update(account_id=client_account_id, gjp=encoded_password)

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def get_timely_info(self, weekly: bool) -> str:
        error_codes = {-1: MissingAccess(f"Can not find {'weekly' if weekly else 'daily'} info.")}

        route = Route(
            POST,
            "/getGJDailyLevel.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            weekly=int(weekly),
            secret=self.get_secret("main"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def download_level(
        self,
        level_id: int,
        *,
        account_id: Optional[int] = None,
        encoded_password: Optional[str] = None,
    ) -> str:
        error_codes = {-1: MissingAccess(f"Can not download level with ID: {level_id}.")}

        route = Route(
            POST,
            "/downloadGJLevel22.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            secret=self.get_secret("main"),
            to_camel=True,
        )

        if account_id is not None and encoded_password is not None:
            inc = 1
            rs = generate_rs()
            udid = self.generate_udid()
            uuid = self.generate_uuid()

            chk = generate_chk(
                values=[level_id, inc, rs, account_id, udid, uuid],
                key=Key.LEVEL,  # type: ignore
                salt=Salt.LEVEL,  # type: ignore
            )

            route.update(
                account_id=account_id,
                gjp=encoded_password,
                udid=udid,
                uuid=uuid,
                rs=rs,
                chk=chk,
                to_camel=True,
            )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def report_level(self, level_id: int) -> int:
        error_codes = {-1: MissingAccess(f"Failed to report level with ID: {level_id}.")}

        route = Route(POST, "/reportGJLevel.php", level_id=level_id, to_camel=True)

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def delete_level(self, level_id: int, *, account_id: int, encoded_password: str) -> int:
        error_codes = {-1: MissingAccess(f"Failed to delete level with ID: {level_id}.")}

        route = Route(
            POST,
            "/deleteGJLevelUser20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            account_id=account_id,
            gjp=encoded_password,
            secret=self.get_secret("level"),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

    async def update_level_description(
        self, level_id: int, description: str, *, account_id: int, encoded_password: str
    ) -> int:
        error_codes = {-1: MissingAccess(f"Can not update description of the level: {level_id}.")}

        route = Route(
            POST,
            "/updateGJDesc20.php",
            game_version=self.get_game_version(),
            binary_version=self.get_binary_version(),
            gdw=self.get_gd_world(),
            level_id=level_id,
            account_id=account_id,
            gjp=encoded_password,
            level_desc=encode_base64_str(description),
            to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return int_or(cast(str, response), 0)

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
        self, level_id: int, stars: int, feature: bool, *, account_id: int, encoded_password: str,
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
        self, account_id: int, unblock: bool, *, client_account_id: int, encoded_password: str,
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
        self, message_id: int, type: MessageType, *, account_id: int, encoded_password: str,
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
        self, message_id: int, type: MessageType, *, account_id: int, encoded_password: str,
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
        self, type: FriendRequestType, page: int, *, account_id: int, encoded_password: str,
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
        self, level_id: int, amount: int, page: int = 0, *, strategy: CommentStrategy,
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

    async def get_ng_song(self, song_id: int) -> str:
        response = await self.request(GET, NEWGROUNDS_SONG_LISTEN.format(song_id=song_id))
        return cast(str, response).replace("\\", "")

    async def get_artist_info(self, song_id: int) -> str:
        error_codes = {-1: MissingAccess(f"Failed to fetch artist info for ID: {song_id}")}

        route = Route(
            GET, "/testSong.php", song_id=song_id, are_params=True, to_camel=True,
        )

        response = await self.request_route(route, error_codes=error_codes)

        return cast(str, response)

    async def search_ng_songs_on_page(self, query: str, page: int = 0) -> str:
        response = await self.request(
            GET, NEWGROUNDS_SEARCH.format(type="audio"), params=dict(terms=query, page=page + 1),
        )

        return cast(str, response)

    async def search_ng_users_on_page(self, query: str, page: int = 0) -> str:
        response = await self.request(
            GET, NEWGROUNDS_SEARCH.format(type="users"), params=dict(terms=query, page=page + 1),
        )

        return cast(str, response)

    async def get_ng_user_songs_on_page(self, name: str, page: int = 0) -> Mapping[str, Any]:
        response = await self.request(
            GET,
            NEWGROUNDS_SONG_PAGE.format(name=name, page=page + 1),
            json=True,
            headers={"X-Requested-With": XML_HTTP_REQUEST},
        )

        return cast(Mapping[str, Any], response)


class HTTPClientContextManager:
    def __init__(self, http_client: HTTPClient, **attrs) -> None:
        self.attrs = attrs
        self.saved_attrs: Dict[str, Any] = {}
        self.http_client = http_client

    def __repr__(self) -> str:
        info = {"http_client": self.http_client}
        info.update(self.attrs)
        return make_repr(self, info)

    def apply(self) -> None:
        http_client = self.http_client
        attrs = self.attrs
        saved_attrs = self.saved_attrs

        for attr, value in attrs.items():
            saved_attrs[attr] = getattr(http_client, attr, None)  # save attribute value
            setattr(http_client, attr, value)  # update attribute value

    def discard(self) -> None:
        http_client = self.http_client
        saved_attrs = self.saved_attrs

        for saved_attr, saved_value in saved_attrs.items():
            setattr(http_client, saved_attr, saved_value)  # restore old attribute values

    def __enter__(self) -> HTTPClient:
        self.apply()

        return self.http_client

    def __exit__(
        self, error_type: Type[BaseException], error: BaseException, traceback: types.TracebackType
    ) -> None:
        self.discard()
