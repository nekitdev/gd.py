'''
import asyncio
import functools
import json
import platform
import re
import secrets
import time

from pathlib import Path

from aiohttp import web
import aiohttp
import multidict

from gd.typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)
import gd

AUTH_RE = re.compile(r"(?:Token )?(?P<token>[A-Fa-z0-9]+)")
CHUNK_SIZE = 64 * 1024
CLIENT = gd.Client()
JSON_PREFIX = "json_"

ROOT_PATH = Path(".gd")

Handler = Callable[[web.Request], Awaitable[web.Response]]
T = TypeVar("T")
U = TypeVar("U")

routes = web.RouteTableDef()


class ErrorType(gd.Enum):
    DEFAULT = 13000
    INVALID_TYPE = 13001
    MISSING_PARAMETER = 13002
    ACCESS_RESTRICTED = 13003
    NOT_FOUND = 13004
    FAILED = 13005
    LOGIN_FAILED = 13006
    RATE_LIMIT_EXCEEDED = 13007
    AUTH_INVALID = 13101
    AUTH_MISSING = 13102
    AUTH_NOT_SET = 13103


class Error:
    def __init__(
        self,
        resp_code: int,
        message: str,
        error_type: Union[int, str, ErrorType] = ErrorType.DEFAULT,
        **additional,
    ) -> None:
        error_type = ErrorType.from_value(error_type)

        self.payload = {
            "status": resp_code,
            "data": {
                "message": message,
                "code": error_type.value,
                "code_name": error_type.title,
                "error": None,
                "error_message": None,
                **additional,
            },
        }

    def set_error(self, error: BaseException) -> "Error":
        to_add = {
            # format message with error object
            "message": self.payload["data"]["message"].format(error=error),
            "error": type(error).__name__,
            "error_message": str(error),
        }
        self.payload["data"].update(to_add)
        return self

    def into_resp(self, **kwargs) -> web.Response:
        return json_resp(**self.payload, **kwargs)


def create_retry_after(retry_after: float) -> Error:
    return Error(
        429,
        f"Retry after {retry_after:.2f} seconds.",
        ErrorType.RATE_LIMIT_EXCEEDED,
        retry_after=retry_after,
    )


DEFAULT_ERROR = Error(
    500,
    (
        "Unexcepted error has occured. "
        "If you think this is a bug, please report it. "
        "Link: [https://github.com/nekitdev/gd.py/issues]"
    ),
    ErrorType.DEFAULT,
)
AUTH_NOT_SET = Error(401, "Authorization header is not set.", ErrorType.AUTH_NOT_SET)
AUTH_INVALID = Error(401, "Authorization token is incorrect.", ErrorType.AUTH_INVALID)
AUTH_MISSING = Error(401, "Authorization token is not found in database.", ErrorType.AUTH_MISSING)


class TokenInfo:
    def __init__(self, name: str, password: str, account_id: int, id: int) -> None:
        self.name = name
        self.password = password
        self.account_id = account_id
        self.id = id
        # generate 256-bit token (32 bytes -> 256 bits)
        self.token = secrets.token_hex(32)

    def __repr__(self) -> str:
        info = {
            "token": repr(self.token),
            "name": repr(self.name),
            "account_id": self.account_id,
            "id": self.id,
        }
        return gd.utils.make_repr(self, info)

    def as_dict(
        self, include: Sequence[str] = ("token", "account_id", "id", "name", "password")
    ) -> Dict[str, Union[int, str]]:
        return {name: getattr(self, name) for name in include}

    def apply_to_client(self, client: gd.Client) -> None:
        # apply state of self to a given client
        client.edit(name=self.name, password=self.password, account_id=self.account_id, id=self.id)


class LoginManager:
    def __init__(self, client: gd.Client, info: TokenInfo) -> None:
        self.client = client
        self.info = info

    def __enter__(self) -> None:
        self.info.apply_to_client(self.client)

    def __exit__(self, *exception) -> None:
        self.client.close()


# class Forward:
    # def __init__(self, client: gd.Client, request: web.Request) -> None:
        # self.http = client.http
        # self.forwarded_for = request.remote
        # self.backup = self.http.forwarded_for

    # def __enter__(self) -> None:
        # self.http.forwarded_for = self.forwarded_for

    # def __exit__(self, *exception) -> None:
        # self.http.forwarded_for = self.backup


# @web.middleware
# async def forward_middleware(request: web.Request, handler: Handler) -> web.Response:
    # with Forward(client=request.app.client, request=request):
        # return await handler(request)


def get_original_handler(handler: Handler) -> Handler:
    while hasattr(handler, "keywords"):
        handler = handler.keywords.get("handler")
    return handler


def get_token(request: web.Request, required: bool) -> Optional[Union[TokenInfo, Error]]:
    # try to get token from Authorization header
    auth = request.headers.get("Authorization")
    if auth is None:
        # try to get token from query
        auth = request.query.get("token")
        if auth is None:
            if required:
                return AUTH_NOT_SET
            return

        # see if token matches pattern
        match = AUTH_RE.match(auth)
        if match is None:
            if required:
                return AUTH_INVALID
            return

        token = match.group("token")

        # check if token is in app.tokens
        token_info = gd.utils.get(request.app.tokens, token=token)
        if token_info is None:
            if required:
                return AUTH_MISSING
            return

        return token_info


@web.middleware
async def auth_middleware(request: web.Request, handler: Handler) -> web.Response:
    original = get_original_handler(handler)
    required = getattr(original, "required", False)

    result = get_token(request, required=required)

    if isinstance(result, Error):
        return result.into_resp()

    request.token_info = result

    # if token is supplied, wrap handling into context manager
    if request.token_info:
        with LoginManager(client=request.app.client, info=request.token_info):
            return await handler(request)

    return await handler(request)


class Cooldown:
    def __init__(self, rate: int, per: float) -> None:
        self.rate = int(rate)
        self.per = float(per)
        self.last = 0.0
        self.tokens = self.rate
        self.window = 0.0

    def copy(self) -> "Cooldown":
        return self.__class__(self.rate, self.per)

    def update_tokens(self, current: Optional[float] = None) -> None:
        if not current:
            current = time.time()

        if current > self.window + self.per:
            self.tokens = self.rate  # reset token state

    def update_rate_limit(self, current: Optional[float] = None) -> Optional[float]:
        if not current:
            current = time.time()

        self.last = current  # may be used externally

        self.update_tokens()

        if self.tokens == self.rate:  # first iteration after reset
            self.window = current  # update window to current

        if not self.tokens:  # rate limited -> return retry_after
            return self.per - (current - self.window)

        self.tokens -= 1  # not rate limited -> decrement tokens

        # if we got rate limited due to this token change,
        # update the window to point to our current time frame
        if not self.tokens:
            self.window = current


class CooldownMapping:
    def __init__(self, original: Cooldown) -> None:
        self.cache: Dict[str, Cooldown] = {}
        self.original = original

    def copy(self) -> "CooldownMapping":
        self_copy = self.__class__(self.original)
        self_copy.cache = self.cache.copy()
        return self_copy

    def clear_unused_cache(self, current: Optional[float] = None) -> None:
        if not current:
            current = time.time()

        self.cache = {
            key: value for key, value in self.cache.items() if current < value.last + value.per
        }

    def construct_key(self, request: web.Request) -> str:
        return "#".join(map(str, (request.remote, request.path)))

    def get_bucket(self, request: web.Request, current: Optional[float] = None) -> Cooldown:
        self.clear_unused_cache()

        key = self.construct_key(request)

        if key in self.cache:
            bucket = self.cache[key]
        else:
            bucket = self.original.copy()
            self.cache[key] = bucket

        return bucket

    def update_rate_limit(
        self, request: web.Request, current: Optional[float] = None
    ) -> Optional[float]:
        bucket = self.get_bucket(request, current)
        return bucket.update_rate_limit(current)

    @classmethod
    def from_cooldown(cls, rate: int, per: float) -> "CooldownMapping":
        return cls(Cooldown(rate, per))


def cooldown(rate: int, per: float) -> Handler:
    def decorator(func: Handler) -> Handler:
        func.cooldown = CooldownMapping.from_cooldown(rate, per)
        return func

    return decorator


@web.middleware
async def error_middleware(request: web.Request, handler: Handler) -> web.Response:
    try:
        return await handler(request)
    except web.HTTPError as error:
        return Error(error.status, "{error.status}: {error.reason}").set_error(error).into_resp()


@web.middleware
async def rate_limit_middleware(request: web.Request, handler: Handler) -> web.Response:
    cooldown = getattr(get_original_handler(handler), "cooldown", None)

    if cooldown:
        retry_after = cooldown.update_rate_limit(request)

        if retry_after:
            retry_after = round(retry_after, 5)
            return create_retry_after(retry_after).into_resp(
                headers={"Retry-After": str(retry_after)}
            )

    return await handler(request)


DEFAULT_MIDDLEWARES = [
    rate_limit_middleware,
    auth_middleware,
    # forward_middleware,
    error_middleware,
    web.normalize_path_middleware(append_slash=False, remove_slash=True),
]


def parse_string(string: Optional[str]) -> Dict[str, Union[Dict[Union[str, int], str], str]]:
    if string is None:
        return {}

    current_section = ""
    current_content = None
    result = {}

    lines = [line for line in string.strip().splitlines() if line] + [""]
    result["method"], result["path"] = lines.pop(0).strip().split(maxsplit=1)

    for line in lines:
        line = line.strip(". ;")
        if line.endswith(":") or not line:
            if current_section:
                if isinstance(current_content, list):
                    current_content = "\n".join(current_content)

                result[current_section] = current_content
                current_content = None

            current_section = line.lower().rstrip(":").replace(" ", "_")

        else:
            key, sep, value = line.partition(": ")

            if sep:
                if current_content is None:
                    current_content = {}

                current_content[key] = value

            else:
                if current_content is None:
                    current_content = []

                current_content.append(line)

    return result


def json_resp(*args, **kwargs) -> web.Response:
    actual_kwargs, json_kwargs = {}, {}

    for key, value in kwargs.items():
        if key.startswith(JSON_PREFIX):
            key = key[len(JSON_PREFIX) :]
            json_kwargs[key] = value
        else:
            actual_kwargs[key] = value

    json_kwargs.setdefault("indent", 4)
    dumps = functools.partial(gd.utils.dumps, **json_kwargs)
    actual_kwargs.setdefault("dumps", dumps)

    return web.json_response(*args, **actual_kwargs)


def create_app(**kwargs) -> web.Application:
    kwargs.update(middlewares=(kwargs.get("middlewares", []) + DEFAULT_MIDDLEWARES))

    if not ROOT_PATH.exists():
        ROOT_PATH.mkdir()

    app = web.Application(**kwargs)
    app.client = kwargs.get("client", CLIENT)
    app.tokens: List[TokenInfo] = []
    app.add_routes(routes)

    return app


def run(app: web.Application, **kwargs) -> None:
    web.run_app(app, **kwargs)


def start(**kwargs) -> None:
    run(create_app(), **kwargs)


def handle_errors(error_dict: Optional[Dict[Type[BaseException], Error]] = None) -> Handler:
    if error_dict is None:
        error_dict = {}

    def decorator(func: Handler) -> Handler:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> web.Response:
            try:
                return await func(*args, **kwargs)

            except BaseException as error:
                return error_dict.get(type(error), DEFAULT_ERROR).set_error(error).into_resp()

        return wrapper

    return decorator


def auth_setup(required: bool = True) -> Handler:
    def decorator(func: Handler) -> Handler:
        func.required = required
        return func

    return decorator


def str_to_bool(
    string: str,
    true: Iterable[str] = {"yes", "y", "true", "t", "1"},
    false: Iterable[str] = {"no", "n", "false", "f", "0"},
) -> bool:
    string = string.casefold()
    if string in true:
        return True
    elif string in false:
        return False
    else:
        raise ValueError(f"Invalid string given: {string!r}.")


def string_to_enum(string: str, enum: gd.Enum) -> gd.Enum:
    if string.isdigit():
        return enum.from_value(int(string))
    return enum.from_value(string)


def get_value(parameter: str, function: Callable[[U], T], default: T, request: web.Request) -> T:
    value = request.query.get(parameter)
    if value is None:
        value = default
    else:
        value = function(value)
    return value


def get_id_and_special(
    item_type: str, item_id: int = 0, level_id: int = 0
) -> Optional[Tuple[int, int]]:
    mapping = {  # string_type: (int_type, special)
        "level": (1, 0),
        "level_comment": (2, level_id),
        "comment": (3, item_id),
    }
    return mapping.get(item_type.casefold().replace(" ", "_"), None)


def parse_route_docs() -> Generator[Dict[str, Union[Dict[Union[str, int], str], str]], None, None]:
    for route in routes:
        info = dict(name=route.handler.__name__)
        info.update(parse_string(route.handler.__doc__))
        yield info


async def delete_after(seconds: float, path: Path) -> None:
    await asyncio.sleep(seconds)

    try:
        path.unlink()
    except Exception:  # noqa
        pass


@routes.get("/api")
@handle_errors()
@auth_setup(required=False)
async def main_page(request: web.Request) -> web.Response:
    """GET /api
    Description:
        Return simple JSON with useful info.
    Example:
        link: /api
    Returns:
        200: JSON with API info.
    Return Type:
        application/json
    """
    payload = {
        "aiohttp": aiohttp.__version__,
        "gd.py": gd.__version__,
        "python": platform.python_version(),
        "routes": list(parse_route_docs()),
    }

    return json_resp(payload)


@routes.post("/api/logout")
@handle_errors()
@auth_setup(required=True)
async def logout_handle(request: web.Request) -> web.Response:
    """POST /api/logout
    Description:
        Log out of the system, deleting the token from the database.
    Example:
        link: /api/logout?token=01a2345678b9012345cd6e7fa8bc9cfab01234c56def7a89bc0de1fab234c56d
        token: 01a2345678b9012345cd6e7fa8bc9cfab01234c56def7a89bc0de1fab234c56d
    Returns:
        200: Empty JSON.
    Return Type:
        application/json
    """
    try:
        request.app.tokens.remove(request.token_info)
    except ValueError:
        pass  # not in tokens, ignore

    return json_resp({})


@routes.get("/api/login")
@handle_errors(
    {
        KeyError: Error(400, "Parameter is missing.", ErrorType.MISSING_PARAMETER),
        gd.LoginFailure: Error(401, "Failed to login.", ErrorType.LOGIN_FAILED),
    }
)
@auth_setup(required=False)
async def auth_handle(request: web.Request) -> web.Response:
    """GET /api/login
    Description:
        Login into API system and get the token for further operation.
    Example:
        link: /api/login?name=User&password=Password
        name: User
        password: Password
    Returns:
        Token for further requests, like {"token": "..."}.
    Return Type:
        application/json
    """
    name = request.query["name"]
    password = request.query["password"]

    # Do NOT use gd.Client.login(...) as it changes state and we do not want this
    account_id, id = await request.app.client.session.login(name, password)

    # Check if name and password are in the app.tokens
    token_info = gd.utils.get(request.app.tokens, name=name, password=password)

    # Create token info object to store current state if not existing
    if token_info is None:
        tokens = set(set_token.token for set_token in request.app.tokens)

        while not token_info or token_info.token in tokens:
            token_info = TokenInfo(name=name, password=password, account_id=account_id, id=id)

        request.app.tokens.append(token_info)

        new = True
    else:
        new = False

    return json_resp({"token": token_info.token, "new": new})


@routes.get("/api/user/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Requested user not found.", ErrorType.NOT_FOUND),
    }
)
@auth_setup(required=False)
async def user_get(request: web.Request) -> web.Response:
    """GET /api/user/{id}
    Description:
        Fetch a user by their Account ID.
    Example:
        link: /api/user/71
    Returns:
        200: JSON with user info;
        400: Invalid type;
        404: User was not found.
    Return Type:
        application/json
    """
    query = int(request.match_info["id"])
    small = str_to_bool(request.query.get("small", "false"))

    if small:
        user = await request.app.client.fetch_user(query)
    else:
        user = await request.app.client.get_user(query)

    return json_resp(user)


@routes.get("/api/song/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Requested song not found.", ErrorType.NOT_FOUND),
        gd.SongRestricted: Error(
            403, "Song is not allowed for use.", ErrorType.ACCESS_RESTRICTED
        ),
    }
)
@auth_setup(required=False)
async def song_search(request: web.Request) -> web.Response:
    """GET /api/song/{id}
    Description:
        Fetch a song by its ID.
    Example:
        link: /api/song/1
    Returns:
        200: JSON with song info;
        400: Invalid type in payload;
        403: Song is not allowed to use;
        404: Song was not found.
    Return Type:
        application/json
    """
    query = int(request.match_info["id"])
    song = await request.app.client.get_song(query)
    return json_resp(song)


@routes.get("/api/song/{id}/info")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Requested artist info was not found", ErrorType.NOT_FOUND),
    }
)
@auth_setup(required=False)
async def get_artist_info(request: web.Request) -> web.Response:
    """GET /api/song/{id}/info
    Description:
        Get information about the song and its artist.
    Example:
        link: /api/song/467339/info
    Returns:
        200: JSON with song and artist info;
        400: Invalid type in payload;
        404: Requested info was not found.
    Return Type:
        application/json
    """
    query = int(request.match_info["id"])
    artist_info = await request.app.client.get_artist_info(query)
    return json_resp(artist_info)


@routes.get("/api/search/user/{query}")
@handle_errors({gd.MissingAccess: Error(404, "Requested user was not found.", ErrorType.NOT_FOUND)})
@auth_setup(required=False)
async def user_search(request: web.Request) -> web.Response:
    """GET /api/search/user/{query}
    Description:
        Fetch a user by their name or player ID.
    Example:
        link: /api/search/user/RobTop
    Returns:
        200: JSON with user info;
        404: User was not found.
    Return Type:
        application/json
    """
    query = request.match_info["query"]
    small = str_to_bool(request.query.get("small", "false"))

    if small:
        user = await request.app.client.find_user(query)
    else:
        user = await request.app.client.search_user(query)

    return json_resp(user)


@routes.get("/api/level/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Requested level was not found", ErrorType.NOT_FOUND),
    }
)
@auth_setup(required=False)
async def get_level(request: web.Request) -> web.Response:
    """GET /api/level/{id}
    Description:
        Fetch a level by given ID.
    Example:
        link: /api/level/30029017
    Returns:
        200: JSON with level info;
        400: Invalid type;
        404: Level was not found.
    Return Type:
        application/json
    """
    level_id = int(request.match_info["id"])
    level = await request.app.client.get_level(level_id)
    return json_resp(level)


@routes.delete("/api/level/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to delete a level.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def delete_level(request: web.Request) -> web.Response:
    """DELETE /api/level/{id}
    Description:
        Delete a level by given ID.
    Example:
        link: /api/level/1234567890
    Returns:
        200: Empty JSON dictionary;
        400: Invalid type;
        404: Failed to delete level.
    Return Type:
        application/json
    """
    level_id = int(request.match_info["id"])

    await gd.Level(id=level_id, client=request.app.client).delete()
    return json_resp({})


@routes.get("/api/install/song/{song_id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Requested song not found.", ErrorType.NOT_FOUND),
    }
)
@auth_setup(required=False)
async def download_song(request: web.Request) -> web.FileResponse:
    """GET /api/install/song/{song_id}
    Description:
        Download a song by its ID.
    Example:
        link: /api/install/song/905110
    Returns:
        200: Found song;
        400: Invalid type;
        404: Failed to find the song.
    Return Type:
        audio/mpeg
    """
    song_id = int(request.match_info["song_id"])

    path = ROOT_PATH / f"song-{song_id}.mp3"

    if path.exists():
        return web.FileResponse(path)

    song = await request.app.client.get_ng_song(song_id)
    await song.download(file=path)

    request.loop.create_task(delete_after(60, path))

    return web.FileResponse(path)


@routes.get("/api/install/level/{level_id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Requested level was not found.", ErrorType.NOT_FOUND),
    }
)
@auth_setup(required=False)
@cooldown(rate=10, per=50)
async def download_level(request: web.Request) -> web.Response:
    """GET /api/install/level/{level_id}
    Description:
        Download a level by its ID, optionally parsing it.
    Example:
        link: /api/install/level/30029017?state=parsed
        state: parsed
    Parameters:
        state: State of level to return. Either "raw", "parsed" (default) or "editor".
    Returns:
        200: JSON with data;
        400: Invalid type;
        404: Level was not found.
    Return Type:
        application/json
    """
    level_id = int(request.match_info["level_id"])
    # "raw", "parsed", "editor"
    state = request.query.get("state", "parsed").casefold()

    level = await request.app.client.get_level(level_id)

    if state == "raw":
        data = gd.Coder.zip(level.data)
        separators = None
    elif state == "editor":
        data = level.open_editor()
        separators = (",", ":")
    else:
        data = level.data
        separators = None

    return json_resp({"data": data}, json_indent=None, json_separators=separators)


@routes.get("/api/daily")
@handle_errors(
    {gd.MissingAccess: Error(404, "Daily is likely being refreshed.", ErrorType.NOT_FOUND)}
)
@auth_setup(required=False)
async def get_daily(request: web.Request) -> web.Response:
    """GET /api/daily
    Description:
        Fetch current daily level.
    Example:
        link: /api/daily
    Returns:
        200: JSON with daily info;
        404: Daily is being refreshed.
    Return Type:
        application/json
    """
    daily = await request.app.client.get_daily()
    return json_resp(daily)


@routes.get("/api/weekly")
@handle_errors(
    {gd.MissingAccess: Error(404, "Weekly is likely being refreshed.", ErrorType.NOT_FOUND)}
)
@auth_setup(required=False)
async def get_weekly(request: web.Request) -> web.Response:
    """GET /api/weekly
    Description:
        Fetch current weekly level.
    Example:
        link: /api/weekly
    Returns:
        200: JSON with weekly info;
        404: Weekly is being refreshed.
    Return Type:
        application/json
    """
    weekly = await request.app.client.get_weekly()
    return json_resp(weekly)


@routes.get("/api/gauntlets")
@handle_errors({gd.MissingAccess: Error(404, "Failed to load gauntlets.", ErrorType.FAILED)})
@auth_setup(required=False)
async def get_gauntlets(request: web.Request) -> web.Response:
    """GET /api/gauntlets
    Description:
        Get all gauntlets and optionally load their levels.
    Example:
        link: /api/gauntlets?load=true
        load: true
    Parameters:
        load: Whether to load gauntlet levels, "true" (default) or "false".
    Returns:
        200: JSON with gauntlets;
        404: Failed to load gauntlets.
    Return Type:
        application/json
    """
    gauntlets = await request.app.client.get_gauntlets()
    load = str_to_bool(request.query.get("load", "true"))

    if load:
        await gd.utils.gather(gauntlet.get_levels() for gauntlet in gauntlets)

    return json_resp(gauntlets)


@routes.get("/api/map_packs")
@handle_errors({gd.MissingAccess: Error(404, "Failed to load map packs.", ErrorType.FAILED)})
@auth_setup(required=False)
async def get_map_packs(request: web.Request) -> web.Response:
    """GET /api/map_packs
    Description:
        Get all map packs and optionally load their levels.
    Example:
        link: /api/map_packs?load=false
        load: false
    Parameters:
        load: Whether to load map pack levels, "true" (default) or "false".
    Returns:
        200: JSON with map packs;
        404: Failed to load map packs.
    Return Type:
        application/json
    """
    pages = map(int, request.query.get("pages", "0").split(","))
    load = str_to_bool(request.query.get("load", "true"))

    map_packs = await request.app.client.get_map_packs(pages=pages)

    if load:
        await gd.utils.gather(map_pack.get_levels() for map_pack in map_packs)

    return json_resp(map_packs)


UPLOAD_QUERY: Dict[str, Tuple[Union[Callable[[str], Any], Any]]] = {
    "name": (str, "Unnamed"),
    "id": (int, 0),
    "version": (int, 1),
    "length": (functools.partial(string_to_enum, enum=gd.LevelLength), gd.LevelLength.TINY),
    "track": (int, 0),
    "song_id": (int, 0),
    "is_auto": (str_to_bool, False),
    "original": (int, 0),
    "two_player": (str_to_bool, False),
    "objects": (int, None),
    "coins": (int, 0),
    "star_amount": (int, 0),
    "unlisted": (str_to_bool, False),
    "friends_only": (str_to_bool, False),
    "ldm": (str_to_bool, False),
    "password": (int, None),
    "copyable": (str_to_bool, False),
    "data": (str, ""),
    "description": (str, ""),
    "load": (str_to_bool, True),
}


@routes.post("/api/level")
@handle_errors({gd.MissingAccess: Error(404, "Failed to upload a level.", ErrorType.FAILED)})
@auth_setup(required=True)
@cooldown(rate=10, per=50)
async def upload_level(request: web.Request) -> web.Response:
    """POST /api/level
    Description:
        Upload a level with given arguments.
    Example:
        link: /api/level?name=Test&track=35&password=123456
        name: Test
        track: 35
        password: 123456
    Parameters:
        name: Name of the level;
        id: ID of the level. 0 if uploading a new level, non-zero to update;
        version: Version of the level;
        length: Length of the level;
        track: Normal track to set, starting from 0 - Stereo Madness;
        song_id: ID of the custom song to set;
        is_auto: Indicates if the level is auto;
        original: ID of the original level;
        two_player: Indicates whether the level has enabled Two Player mode;
        objects: The amount of objects in the level;
        coins: Amount of coins the level has;
        star_amount: The amount of stars to request;
        unlist: Indicates whether the level should be unlisted;
        ldm: Indicates if the level has LDM mode;
        password: The password to apply;
        copyable: Indicates whether the level should be copyable;
        data: The data of the level, as a string;
        description: The description of the level.
    Returns:
        200: JSON with uploaded level;
        404: Failed to upload level.
    Return Type:
        application/json
    """
    upload_arguments = {
        parameter: get_value(parameter, function, default, request)
        for (parameter, (function, default)) in UPLOAD_QUERY.items()
    }

    level = await request.app.client.upload_level(**upload_arguments)

    return json_resp(level)


@routes.get("/api/chests")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get chests.", ErrorType.FAILED)})
@auth_setup(required=True)
async def get_chests(request: web.Request) -> web.Response:
    """GET /api/chests
    Description:
        Load chests of the connected client.
    Example:
        link: /api/chests
    Returns:
        200: JSON with chests;
        404: Failed to get chests.
    Return Type:
        application/json
    """
    chests = await request.app.client.get_chests()
    return json_resp(chests)


@routes.get("/api/quests")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get quests.", ErrorType.FAILED)})
@auth_setup(required=True)
async def get_quests(request: web.Request) -> web.Response:
    """GET /api/quests
    Description:
        Load quests of the connected client.
    Example:
        link: /api/quests
    Returns:
        200: JSON with quests;
        404: Failed to get quests.
    Return Type:
        application/json
    """
    quests = await request.app.client.get_quests()
    return json_resp(quests)


@routes.get("/api/levels")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get levels.", ErrorType.FAILED)})
@auth_setup(required=True)
async def get_levels(request: web.Request) -> web.Response:
    """GET /api/levels
    Description:
        Load levels of the connected client.
    Example:
        link: /api/levels?pages=0,1,2,3
        pages: 0,1,2,3
    Parameters:
        pages: Pages of levels to load.
    Returns:
        200: JSON with levels;
        404: Failed to get levels.
    Return Type:
        application/json
    """
    pages = map(int, request.query.get("pages", "0").split(","))
    levels = await request.app.client.get_levels(pages=pages)
    return json_resp(levels)


@routes.get("/api/messages")
@handle_errors({gd.MissingAccess: Error(404, "Failed to load messages.", ErrorType.FAILED)})
@auth_setup(required=True)
async def get_messages(request: web.Request) -> web.Response:
    """GET api/messages
    Description:
        Load messages, optionally reading them.
    Example:
        link: /api/messages?pages=0,1,2,3&sent=false&read=true
        pages: 0,1,2,3
        sent: false
        read: true
    Parameters:
        pages: Pages of messages to load;
        sent: Whether to load sent messages, "true" or "false" (default);
        read: Whether to read messages, "true" (default) or "false".
    Returns:
        200: JSON with messages;
        404: Failed to load messages.
    Return Type:
        application/json
    """
    pages = map(int, request.query.get("pages", "0").split(","))
    sent = str_to_bool(request.query.get("sent", "false"))
    read = str_to_bool(request.query.get("read", "true"))
    sent_or_inbox = "sent" if sent else "inbox"

    messages = await request.app.client.get_messages(sent_or_inbox, pages=pages)

    if read:
        await gd.utils.gather(message.read() for message in messages)

    return json_resp(messages)


@routes.get("/api/message/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to read a message.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def read_message(request: web.Request) -> web.Response:
    """GET /api/message/{id}
    Description:
        Read a message by its ID.
    Example:
        link: /api/message/123456789
    Parameters:
        type: Type of the message, either "sent" or "normal" (default).
    Returns:
        200: JSON with message body;
        404: Failed to read a message.
    Return Type:
        application/json
    """
    message_id = int(request.match_info["id"])
    message_type = string_to_enum(request.query.get("type", "normal"), gd.MessageType)

    body = await gd.Message(id=message_id, type=message_type, client=request.app.client).read()

    return json_resp({"body": body})


@routes.delete("/api/message/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to delete a message.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def delete_message(request: web.Request) -> web.Response:
    """DELETE /api/message/{id}
    Description:
        Delete a message by its ID.
    Example:
        link: /api/message/123456789
    Parameters:
        type: Type of the message, either "sent" or "normal" (default).
    Returns:
        200: Empty JSON;
        404: Failed to delete a message.
    Return Type:
        application/json
    """
    message_id = int(request.match_info["id"])
    message_type = string_to_enum(request.query.get("type", "normal"), gd.MessageType)

    await gd.Message(id=message_id, type=message_type, client=request.app.client).delete()

    return json_resp({})


@routes.get("/api/friend_requests")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get friend requests.", ErrorType.FAILED)})
@auth_setup(required=True)
async def get_friend_requests(request: web.Request) -> web.Response:
    """GET api/friend_requests
    Description:
        Load friend requests, optionally reading them.
    Example:
        link: /api/friend_requests?pages=0,1,2,3&sent=false&read=false
        pages: 0,1,2,3
        sent: false
        read: false
    Parameters:
        pages: Pages of friend requests to load;
        sent: Whether to load sent friend requests, "true" or "false" (default);
        read: Whether to read friend requests, "true" (default) or "false".
    Returns:
        200: JSON with friend requests;
        404: Failed to load friend requests.
    Return Type:
        application/json
    """
    pages = map(int, request.query.get("pages", "0").split(","))
    sent = str_to_bool(request.query.get("sent", "false"))
    read = str_to_bool(request.query.get("read", "false"))
    sent_or_inbox = "sent" if sent else "inbox"

    friend_requests = await request.app.client.get_friend_requests(sent_or_inbox, pages=pages)

    if read:
        await gd.utils.gather(friend_request.read() for friend_request in friend_requests)

    return json_resp(friend_requests)


@routes.get("/api/friend_request/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to get a request.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def read_friend_request(request: web.Request) -> web.Response:
    """GET /api/friend_request/{id}
    Description:
        Read friend request by its ID.
    Example:
        link: /api/friend_request/123456789
    Returns:
        200: Empty JSON;
        404: Failed to get a request.
    Return Type:
        application/json
    """
    request_id = int(request.match_info["id"])

    await gd.FriendRequest(id=request_id, client=request.app.client).read()

    return json_resp({})


@routes.delete("/api/friend_request/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to delete a request.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def delete_friend_request(request: web.Request) -> web.Response:
    """DELETE /api/friend_request/{id}
    Description:
        Delete friend request by its ID.
    Example:
        link: /api/friend_request/123456789?type=normal&author_id=987654321
        type: normal
        author_id: 987654321
    Parameters:
        type: Type of friend request, "sent" or "normal" (default);
        author_id: AccountID of the author of friend request.
    Returns:
        200: Empty JSON;
        404: Failed to delete a request.
    Return Type:
        application/json
    """
    request_id = int(request.match_info["id"])
    request_type = string_to_enum(request.query.get("type", "normal"), gd.FriendRequestType)
    account_id = int(request.query["author_id"])

    await gd.FriendRequest(
        author=gd.User(account_id=account_id, client=request.app.client),
        id=request_id,
        type=request_type,
        client=request.app.client,
    ).delete()

    return json_resp({})


@routes.patch("/api/friend_request/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to accept a request.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def accept_friend_request(request: web.Request) -> web.Response:
    """PATCH /api/friend_request/{id}
    Description:
        Accept friend request by its ID.
    Example:
        link: /api/friend_request/123456789?author_id=987654321
        author_id: 987654321
    Parameters:
        type: Type of friend request, "normal" (always);
        author_id: AccountID of the author of friend request.
    Returns:
        200: Empty JSON;
        404: Failed to accept a request.
    Return Type:
        application/json
    """
    request_id = int(request.match_info["id"])
    request_type = string_to_enum(request.query.get("type", "normal"), gd.FriendRequestType)
    account_id = int(request.query["author_id"])

    await gd.FriendRequest(
        author=gd.User(account_id=account_id, client=request.app.client),
        id=request_id,
        type=request_type,
        client=request.app.client,
    ).accept()

    return json_resp({})


@routes.get("/api/friends")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get friends.", ErrorType.FAILED)})
@auth_setup(required=True)
async def get_friends(request: web.Request) -> web.Response:
    """GET /api/friends
    Description:
        Get friend of the connected client.
    Example:
        link: /api/friends
    Returns:
        200: JSON list of friends;
        404: Failed to get friends.
    Return Type:
        application/json
    """
    friends = await request.app.client.get_friends()
    return json_resp(friends)


@routes.patch("/api/{action:(unblock|block)}/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to (un)block user.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def un_block_user(request: web.Request) -> web.Response:
    """PATCH /api/{action:(block|unblock)}/{id}
    Description:
        Block or unblock user by their AccountID.
    Example:
        link: api/unblock/123456789
    Returns:
        200: Empty JSON;
        404: Failed to block or unblock given user.
    Return Type:
        application/json
    """
    account_id = int(request.match_info["id"])
    unblock = request.match_info["action"].startswith("un")

    user = await gd.User(account_id=account_id, client=request.app.client)

    if unblock:
        await user.unblock()
    else:
        await user.block()

    return json_resp({})


@routes.patch("/api/{action:(unfriend|friend)}/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to (un)friend user.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def un_friend_user(request: web.Request) -> web.Response:
    """PATCH /api/{action:(friend|unfriend)}/{id}
    Description:
        Unfriend user or send a friend request to them by their AccountID.
    Example:
        link: api/friend/123456789?message=Hello!
        message: Hello!
    Parameters:
        message: Message to send with friend request. (Ignored if /unfriend/).
    Returns:
        200: Empty JSON or friend request data;
        404: Failed to send a friend request or unfriend given user.
    Return Type:
        application/json
    """
    account_id = int(request.match_info["id"])
    unfriend = request.match_info["action"].startswith("un")
    message = request.query.get("message", "")

    user = gd.User(account_id=account_id, client=request.app.client)

    if unfriend:
        await user.unfriend()
        return json_resp({})
    else:
        friend_request = await user.send_friend_request(message=message)
        return json_resp(friend_request)

    return json_resp({})


@routes.get("/api/blocked")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get blocked users.", ErrorType.FAILED)})
@auth_setup(required=True)
async def get_blocked(request: web.Request) -> web.Response:
    """GET /api/blocked
    Description:
        Get users blocked by the connected client.
    Example:
        link: /api/blocked
    Returns:
        200: JSON list of blocked users;
        404: Failed to get blocked users.
    Return Type:
        application/json
    """
    blocked = await request.app.client.get_blocked_users()
    return json_resp(blocked)


@routes.post("/api/send/{query}")
@handle_errors(
    {
        KeyError: Error(400, "Parameter is missing.", ErrorType.MISSING_PARAMETER),
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "{error}", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
@cooldown(rate=5, per=5)
async def send_message(request: web.Request) -> web.Response:
    """POST /api/send/{query}
    Description:
        Send a message to the user given by the query.
    Example:
        link: /api/send/5509312?id=true&subject=Server&body=Test
        id: true
        subject: Server
        body: Test
    Parameters:
        id: Whether given query is AccountID, "true" or "false" (default);
        subject: Subject of the message to send, "No Subject" by default;
        body: Body of the message to send, required.
    Returns:
        200: JSON with the message;
        404: Failed to send a message.
    Return Type:
        application/json
    """
    query = request.match_info["query"]

    is_id = str_to_bool(request.query.get("id", "false"))

    subject = request.query.get("subject", "No Subject")
    body = request.query["body"]

    if is_id:
        user = await request.app.client.fetch_user(int(query))
    else:
        user = await request.app.client.find_user(query)

    message = await user.send(subject, body)

    return json_resp(message)


@routes.patch("/api/{action:(dislike|like)}/{id}")
@handle_errors(
    {
        KeyError: Error(400, "Parameter is missing.", ErrorType.MISSING_PARAMETER),
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to like an entity.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
@cooldown(rate=5, per=5)
async def like_item(request: web.Request) -> web.Response:
    """PATCH /api/{action:(dislike|like)}/{id}
    Description:
        Like or dislike item given by ID.
    Example:
        link: /api/like/16625059?type=comment
        type: comment
    Parameters:
        type: Type of the item, "comment", "level" or "level_comment". Required;
        level_id: ID of the Level, needed if type is "level_comment".
    Returns:
        200: Empty JSON;
        400: Parameter is missing;
        404: Failed to like an entity.
    Return Type:
        application/json
    """
    dislike = request.match_info["action"].startswith("dis")

    item_id = int(request.match_info["id"])
    item_type = request.query["type"]
    level_id = int(request.query.get("level_id", 0))

    type_id, special = get_id_and_special(item_type, item_id, level_id)

    await request.app.client.session.like(
        item_id, type_id, special, dislike=dislike, client=request.app.client
    )

    return json_resp({})


@routes.patch("/api/level/{id}/rate")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to rate a level.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
@cooldown(rate=5, per=5)
async def rate_level(request: web.Request) -> web.Response:
    """PATCH /api/level/{id}/rate
    Description:
        Rate the level given by its ID.
    Example:
        link: /api/level/44622744/rate?stars=10
        stars: 10
    Parameters:
        stars: Stars to rate the level with, required.
    Returns:
        200: Empty JSON;
        404: Failed to rate a level.
    Return Type:
        application/json
    """
    level_id = int(request.match_info["id"])
    stars = int(request.query["stars"])

    await gd.Level(id=level_id, client=request.app.client).rate(stars)
    return json_resp({})


@routes.patch("/api/level/{id}/description")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to update level description.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def update_level_description(request: web.Request) -> web.Response:
    """PATCH /api/level/{id}/description
    Description:
        Update level description.
    Example:
        link: /api/level/123456789/description?new=Test
        new: Test
    Parameters:
        new: New description to set. If not given, clears current description.
    Returns:
        200: Empty JSON;
        404: Failed to update level description.
    Return Type:
        application/json
    """
    level_id = int(request.match_info["id"])
    new = request.query.get("new", "")

    await gd.Level(id=level_id, client=request.app.client).update_description(new)
    return json_resp({})


@routes.patch("/api/level/{id}/rate_demon")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to demon-rate a level.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def rate_level_demon(request: web.Request) -> web.Response:
    """PATCH /api/level/{id}/rate_demon
    Description:
        Demon-Rate the level given by its ID.
    Example:
        link: /api/level/42584142/rate_demon?difficulty=extreme_demon&mod=false
        difficulty: extreme_demon
        mod: false
    Parameters:
        difficulty: Difficulty to demon-rate the level with, required;
        mod: Whether to attempt to demon-rate the level as mod, "true" or "false" (default).
    Returns:
        200: Empty JSON;
        404: Failed to demon-rate a level.
    Return Type:
        application/json
    """
    level_id = int(request.match_info["id"])
    demon_difficulty = string_to_enum(request.query["difficulty"], gd.DemonDifficulty)
    as_mod = str_to_bool(request.query.get("mod", "false"))

    await gd.Level(id=level_id, client=request.app.client).rate_demon(
        demon_difficulty, as_mod=as_mod
    )

    return json_resp({})


@routes.patch("/api/level/{id}/send")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to send a level.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def send_level(request: web.Request) -> web.Response:
    """PATCH /api/level/{id}/send
    Description:
        Send the level given by its ID for rating.
        Requires Moderator privileges.
    Example:
        link: /api/level/123456789/send?stars=10&feature=true
        stars: 10
        feature: true
    Parameters:
        stars: Stars to send the level with, required;
        mod: Whether to send the level for feature, "true" or "false", required.
    Returns:
        200: Empty JSON;
        404: Failed to send a level.
    Return Type:
        application/json
    """
    level_id = int(request.match_info["id"])
    stars = int(request.query["stars"])
    featured = str_to_bool(request.query["featured"])

    await gd.Level(id=level_id, client=request.app.client).send(stars, featured=featured)

    return json_resp({})


@routes.get("/api/level/{id}/comments")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to get level comments.", ErrorType.FAILED),
    }
)
@auth_setup(required=False)
async def get_level_comments(request: web.Request) -> web.Response:
    """GET /api/level/{id}/comments
    Description:
        Get comments of the level given by its ID.
    Example:
        link: /api/level/30029017/comments?amount=100&strategy=most_liked
        amount: 100
        strategy: most_liked
    Parameters:
        amount: Amount of comments to fetch, 20 by default;
        strategy: Strategy to apply, "recent" (default) or "most_liked".
    Returns:
        200: JSON with level comments;
        404: Failed to get level comments.
    Return Type:
        application/json
    """
    level_id = int(request.match_info["id"])
    amount = int(request.query.get("amount", 20))
    strategy = string_to_enum(request.query.get("strategy", "recent"), gd.CommentStrategy)

    comments = await gd.Level(id=level_id, client=request.app.client).get_comments(
        amount=amount, strategy=strategy
    )

    return json_resp(comments)


@routes.get("/api/level/{id}/leaderboard")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to get the leaderboard.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def get_level_leaderboard(request: web.Request) -> web.Response:
    """GET /api/level/{id}/leaderboard
    Description:
        Get leaderboard of the level given by its ID.
    Example:
        link: /api/level/30029017/leaderboard?strategy=all
        strategy: all
    Parameters:
        strategy: Strategy to apply, "all" (default), "weekly" or "friends".
    Returns:
        200: JSON with level records;
        404: Failed to get the leaderboard.
    Return Type:
        application/json
    """
    level_id = int(request.match_info["id"])
    strategy = string_to_enum(
        request.match_info.get("strategy", "all"), gd.LevelLeaderboardStrategy
    )

    records = await gd.Level(id=level_id, client=request.app.client).get_leaderboard(
        strategy=strategy
    )

    return json_resp(records)


@routes.get("/api/user/{id}/comments")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to get user comments.", ErrorType.FAILED),
    }
)
@auth_setup(required=False)
async def get_user_comments(request: web.Request) -> web.Response:
    """GET /api/user/{id}/comments
    Description:
        Get comments of the user given by AccountID.
    Example:
        link: /api/user/5509312/comments?pages=0,1,2,3&type=profile&strategy=recent
        pages: 0,1,2,3
        type: profile
        strategy: recent
    Parameters:
        pages: Pages of comments to load, e.g. "0,1,2,3";
        type: Type of comments to fetch, either "profile" (default) or "level";
        strategy: Strategy to use for fetching, "recent" (default) or "most_liked".
    Returns:
        200: JSON with found comments;
        404: Failed to get comments.
    Return Type:
        application/json
    """
    account_id = int(request.match_info["id"])
    pages = map(int, request.query.get("pages", "0").split(","))
    type_str = request.query.get("type", "profile")
    strategy = string_to_enum(request.query.get("strategy", "recent"), gd.CommentStrategy)

    user = await request.app.client.fetch_user(account_id)
    comments = await user.retrieve_comments(type=type_str, pages=pages, strategy=strategy)

    return json_resp(comments)


@routes.post("/api/level/{level_id}/comment")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to comment a level.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def comment_level(request: web.Request) -> web.Response:
    """POST /api/level/{level_id}/comment
    Description:
        Post a comment on the level given by Level ID.
    Example:
        link: /api/level/1/comment?body=Test&percentage=42
        body: Test
        percentage: 42
    Parameters:
        body: Body of the comment, required;
        percentage: Percentage to put, 0 by default.
    Returns:
        200: JSON with comment data;
        404: Failed to comment a level.
    Return Type:
        application/json
    """
    level_id = int(request.match_info["level_id"])
    body = request.query["body"]
    percentage = int(request.query.get("percentage", 0))

    comment = await gd.Level(id=level_id, client=request.app.client).comment(body, percentage)

    return json_resp(comment)


@routes.post("/api/comment")
@handle_errors({gd.MissingAccess: Error(404, "Failed to post a comment.", ErrorType.FAILED)})
@auth_setup(required=True)
async def post_comment(request: web.Request) -> web.Response:
    """POST /api/comment
    Description:
        Post a profile comment.
    Example:
        link: /api/comment?body=Test
        body: Test
    Parameters:
        body: Body of the comment to post.
    Returns:
        200: JSON with the comment;
        404: Failed to post a comment.
    Return Type:
        application/json
    """
    body = request.query["body"]

    comment = await request.app.client.post_comment(body)

    return json_resp(comment)


SETTINGS_QUERY: Dict[str, Tuple[Union[Callable[[str], Any], Any]]] = {
    "message_policy": (functools.partial(string_to_enum, enum=gd.MessagePolicyType), None),
    "friend_request_policy": (
        functools.partial(string_to_enum, enum=gd.FriendRequestPolicyType),
        None,
    ),
    "comment_policy": (functools.partial(string_to_enum, enum=gd.CommentPolicyType), None),
    "youtube": (str, None),
    "twitter": (str, None),
    "twitch": (str, None),
}


@routes.patch("/api/settings")
@handle_errors({gd.MissingAccess: Error(404, "Failed to edit settings.", ErrorType.FAILED)})
@auth_setup(required=True)
async def update_settings(request: web.Request) -> web.Response:
    """PATCH /api/settings
    Description:
        Update profile settings, policies and social media links.
    Example:
        link: /api/settings?comment_policy=opened_to_all
        comment_policy: opened_to_all
    Parameters:
        message_policy: Message policy of the account;
        friend_request_policy: Friend Request policy of the account;
        comment_policy: Comment policy of the account;
        youtube: YouTube ID of the channel;
        twitter: Twitter name of the account;
        twitch: Twitch name of the account.
    Returns:
        200: Empty JSON;
        404: Failed to edit settings.
    Return Type:
        application/json
    """
    update_arguments = {
        parameter: get_value(parameter, function, default, request)
        for (parameter, (function, default)) in SETTINGS_QUERY.items()
    }

    await request.app.client.update_settings(**update_arguments)

    return json_resp({})


PROFILE_QUERY: Dict[str, Tuple[Union[Callable[[str], Any], Any]]] = {
    "stars": (int, None),
    "demons": (int, None),
    "diamonds": (int, None),
    "has_glow": (bool, None),
    "icon_type": (functools.partial(string_to_enum, enum=gd.IconType), None),
    "icon": (int, None),
    "color_1": (int, None),
    "color_2": (int, None),
    "coins": (int, None),
    "user_coins": (int, None),
    "cube": (int, None),
    "ship": (int, None),
    "ball": (int, None),
    "ufo": (int, None),
    "wave": (int, None),
    "robot": (int, None),
    "spider": (int, None),
    "explosion": (int, None),
    "special": (int, 0),
    "set_as_user": (str, None),
}


@routes.patch("/api/profile")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to update profile.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def update_profile(request: web.Request) -> web.Response:
    """PATCH /api/profile
    Description:
        Update profile of the connected client.
    Example:
        link: /api/profile?has_glow=true&icon_type=cube&icon=3
        has_glow: true
        icon_type: cube
        icon: 3
    Parameters:
        stars: An amount of stars to set;
        demons: An amount of completed demons to set;
        diamonds: An amount of diamonds to set;
        has_glow: Indicates whether a user should have the glow outline;
        icon_type: Icon type that should be used;
        icon: Icon ID that should be used;
        color_1: Index of a color to use as the main color;
        color_2: Index of a color to use as the secodary color;
        coins: An amount of secret coins to set;
        user_coins: An amount of user coins to set;
        cube: An index of a cube icon to apply;
        ship: An index of a ship icon to apply;
        ball: An index of a ball icon to apply;
        ufo: An index of a ufo icon to apply;
        wave: An index of a wave icon to apply;
        robot: An index of a robot icon to apply;
        spider: An index of a spider icon to apply;
        explosion: An index of an explosion to apply;
        special: The purpose of this parameter is unknown;
        id: Whether to interpret "set_as_user" as AccountID or Name/PlayerID;
        set_as_user: Passing this parameter allows to copy user's profile.
    Returns:
        200: Empty JSON;
        404: Failed to update profile.
    Return Type:
        application/json
    """
    is_id = str_to_bool(request.query.get("id", "false"))

    update_arguments = {
        parameter: get_value(parameter, function, default, request)
        for (parameter, (function, default)) in PROFILE_QUERY.items()
    }

    query = update_arguments.get("set_as_user")

    if query is None:
        user = None
    elif is_id:
        user = await request.app.client.get_user(int(query))
    else:
        user = await request.app.client.search_user(query)

    update_arguments.update(set_as_user=user)

    await request.app.client.update_profile(**update_arguments)

    return json_resp({})


def color_from_hex(string: str) -> gd.Color:
    return gd.Color(int(string.replace("#", "0x"), 16))


@routes.get("/api/icon_factory")
@handle_errors(
    {
        AttributeError: Error(
            500, "Can not generate icons due to factory missing.", ErrorType.NOT_FOUND
        ),
        LookupError: Error(404, "Icon was not found.", ErrorType.NOT_FOUND),
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        Warning: Error(404, "No types to generate are given.", ErrorType.NOT_FOUND),
    }
)
@auth_setup(required=False)
async def generate_icons(request: web.Request) -> web.Response:
    """GET /api/icon_factory
    Description:
        Generate icons according to given query.
    Example:
        link: /api/icon_factory?cube=2&color_1=0x7289da&color_2=0xffffff&glow_outline=true
        cube: 2
        color_1: 0x7289da
        color_2: 0xffffff
        glow_outline: true
    Parameters:
        cube: Cube ID to generate (can be repeated);
        ship: Ship ID to generate (can be repeated);
        ball: Ball ID to generate (can be repeated);
        ufo: UFO ID to generate (can be repeated);
        wave: Wave ID to generate (can be repeated);
        robot: Robot ID to generate (can be repeated);
        spider: Spider ID to generate (can be repeated);
        color_1: Main color to use;
        color_2: Secondary color to use;
        glow_outline: Whether generated icon should have outline;
        error_on_not_found: Whether error should be reported if icon was not found.
    Returns:
        200: Image containing all generated icons in query order;
        400: Invalid type in payload;
        404: Icon was not found or no types were given;
        500: Icon Factory is missing.
    Return Type:
        image/png
    """
    query = multidict.CIMultiDict(request.query)

    color_1 = color_from_hex(query.pop("color_1", "0x00ff00"))
    color_2 = color_from_hex(query.pop("color_2", "0x00ffff"))
    glow_outline = str_to_bool(query.pop("glow_outline", "false"))
    error_on_not_found = str_to_bool(query.pop("error_on_not_found", "false"))

    settings = f"color_1={color_1}$color_2={color_2}$glow_outline={glow_outline}".lower()
    types = "$".join(f"{key}={value}".lower() for key, value in query.items())
    name = f"[{settings}]({types}).png"
    path = ROOT_PATH / name

    if path.exists():
        return web.FileResponse(path)

    images = [
        await gd.utils.run_blocking_io(
            gd.factory.generate,
            icon_type=gd.IconType.from_value(icon_type),
            icon_id=int(icon_id),
            color_1=color_1,
            color_2=color_2,
            glow_outline=glow_outline,
            error_on_not_found=error_on_not_found,
        )
        for icon_type, icon_id in query.items()
    ]

    if not images:
        raise Warning("No types were generated.")

    image = await gd.utils.run_blocking_io(gd.icon_factory.connect_images, images)

    image.save(path)

    request.loop.create_task(delete_after(15, path))

    return web.FileResponse(path)


@routes.get("/api/icons/{type:(all|main|cube|ship|ball|ufo|wave|robot|spider)}/{query}")
@handle_errors(
    {
        AttributeError: Error(
            500, "Can not generate icons due to factory missing.", ErrorType.NOT_FOUND
        ),
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Could not find requested user.", ErrorType.NOT_FOUND),
    }
)
@auth_setup(required=False)
async def get_icons(request: web.Request) -> web.Response:
    """GET /api/icons/{type:(all|main|cube|ship|ball|ufo|wave|robot|spider)}/{query}
    Description:
        Generate icon of the user given by query.
    Example:
        link: /api/icons/all/5509312?id=true
        id: true
    Parameters:
        id: Whether to interpret "query" as AccountID or Name/PlayerID;
    Returns:
        200: Image with generated icons;
        404: Could not find requested user;
        500: Icon Factory is missing.
    Return Type:
        image/png
    """
    icon_type = request.match_info["type"]
    query = request.match_info["query"]

    is_id = str_to_bool(request.query.get("id", "false"))

    if is_id:
        user = await request.app.client.get_user(int(query))
    else:
        user = await request.app.client.search_user(query)

    path = ROOT_PATH / f"icons-{icon_type}-{user.account_id}.png"

    if path.exists():
        return web.FileResponse(path)

    if icon_type == "main":
        icon_type = user.icon_set.main_type.name.lower()

    if icon_type == "all":
        image = await user.icon_set.generate_full(as_image=True)
    else:
        image = await user.icon_set.generate(icon_type, as_image=True)

    image.save(path)

    request.loop.create_task(delete_after(15, path))

    return web.FileResponse(path)


@routes.get("/api/search/levels")
@handle_errors({ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE)})
@auth_setup(required=False)
async def search_levels(request: web.Request) -> web.Response:
    """GET /api/search/levels
    Description:
        Search levels with provided options.
    Example:
        link: /api/search/levels?query=Bloodlust&demon_difficulty=extreme_demon&pages=0
        query: Bloodlust
        demon_difficulty: extreme_demon
    Parameters:
        query: Query to search for, by default empty string;
        pages: Pages to look levels on;
        strategy: Strategy to apply when searching, "regular" by default;
        difficulty: Difficulties to filter levels, optional;
        demon_difficulty: Demon Difficulty to filter levels, optional;
        length: Lengths to filter levels, optional;
        uncompleted: Whether to fetch only uncompleted levels, requires "completed_levels";
        only_completed: Whether to fetch only completed levels, requires "completed_levels";
        completed_levels: Comma-separated list of IDs of completed levels, e.g. "1,2,3,4";
        require_coins: Whether levels should have coins, "false" by default;
        featured: Whether levels should be featured, "false" by default;
        epic: Whether levels should be epic, "false" by default;
        require_two_player: Whether levels should have Two Player mode, "false" by default;
        rated: If not omitted, forces levels to be either rated or unrated strictly;
        song_id: Song ID of the Song/Track to use;
        use_custom_song: Whether Song by given "song_id" is custom or not, "false" by default;
        require_original: Whether to force levels to be original, "false" by default;
        followed: Comma-separated list of IDs of followed users, e.g. "71,5509312";
        gauntlet: ID or Name of the gauntlet to fetch levels of;
        id: Indicates whether to interpret "user" as AccountID or Name/PlayerID;
        user: User to fetch levels from. If not given, logged in account might be required.
    Returns:
        200: JSON with levels;
        404: No levels were found.
    Return Type:
        application/json
    """
    is_id = str_to_bool(request.query.get("id", "false"))
    query = request.query.get("query", "")
    pages = map(int, request.query.get("pages", "0").split(","))
    user_query = request.query.get("user")

    gauntlet = request.query.get("gauntlet")
    if gauntlet is not None:
        if not gauntlet.isdigit():
            gauntlet = gd.Converter.get_gauntlet_id(gauntlet)  # assume name
        else:
            gauntlet = int(gauntlet)

    strategy = string_to_enum(request.query.get("strategy", "0"), gd.SearchStrategy)

    difficulty = request.query.get("difficulty")
    if difficulty is not None:
        difficulty = (string_to_enum(part, gd.LevelDifficulty) for part in difficulty.split(","))

    demon_difficulty = request.query.get("demon_difficulty")
    if demon_difficulty is not None:
        demon_difficulty = string_to_enum(demon_difficulty, gd.DemonDifficulty)

    length = request.query.get("length")
    if length is not None:
        length = (string_to_enum(part, gd.LevelLength) for part in length.split(","))

    uncompleted = str_to_bool(request.query.get("uncompleted", "false"))
    only_completed = str_to_bool(request.query.get("only_completed", "false"))

    completed_levels = request.query.get("completed_levels")
    if completed_levels is not None:
        completed_levels = map(int, completed_levels.split(","))

    require_coins = str_to_bool(request.query.get("require_coins", "false"))

    featured = str_to_bool(request.query.get("featured", "false"))
    epic = str_to_bool(request.query.get("epic", "false"))

    require_two_player = str_to_bool(request.query.get("require_two_player", "false"))

    rated = request.query.get("rated")
    if rated is not None:
        rated = str_to_bool(rated)

    song_id = request.query.get("song_id")
    if song_id is not None:
        song_id = int(song_id)

    use_custom_song = str_to_bool(request.query.get("use_custom_song", "false"))
    require_original = str_to_bool(request.query.get("require_original", "false"))

    followed = request.query.get("followed")
    if followed is not None:
        followed = map(int, followed.split(","))

    if user_query is None:
        user = None
    elif is_id:
        user = await request.app.client.fetch_user(int(user_query))
    else:
        user = await request.app.client.find_user(user_query)

    filters = gd.Filters(
        strategy=strategy,
        difficulty=difficulty,
        demon_difficulty=demon_difficulty,
        length=length,
        uncompleted=uncompleted,
        only_completed=only_completed,
        completed_levels=completed_levels,
        require_coins=require_coins,
        featured=featured,
        epic=epic,
        rated=rated,
        require_two_player=require_two_player,
        song_id=song_id,
        use_custom_song=use_custom_song,
        require_original=require_original,
        followed=followed,
    )

    levels = await request.app.client.search_levels(
        query=query, filters=filters, user=user, gauntlet=gauntlet, pages=pages
    )

    return json_resp(levels)


@routes.get("/api/load")
@handle_errors({gd.MissingAccess: Error(404, "Failed to load the save.", ErrorType.FAILED)})
@auth_setup(required=True)
@cooldown(rate=10, per=100)
async def load_save(request: web.Request) -> web.Response:
    """GET /api/load
    Description:
        Load save and return it as JSON.
    Example:
        link: /api/load
    Returns:
        200: JSON with the save and the database;
        404: Failed to load the save.
    Return Type:
        application/json
    """
    await request.app.client.load()
    return json_resp(
        {"database": request.app.client.db, "save": request.app.client.save},
        json_indent=None,
        json_separators=(",", ":"),
    )


def convert_to_encoded(string: str) -> str:
    try:
        data = gd.api.Part(json.loads(string)).dump()
    except json.JSONDecodeError:
        if "?xml" in string:  # xml
            data = gd.Coder.encode_save(string)
        else:  # assume base64
            data = string

    return data


@routes.patch("/api/save")
@handle_errors({gd.MissingAccess: Error(404, "Failed to save.", ErrorType.FAILED)})
@auth_setup(required=True)
@cooldown(rate=10, per=100)
async def backup_save(request: web.Request) -> web.Response:
    """PATCH /api/save
    Description:
        Request save backup with given main and levels parts.
    Example:
        link: /api/save?main=MAIN&levels=LEVELS
        main: MAIN
        levels: LEVELS
    Parameters:
        main: Main part of the save (CCGameManager.dat). JSON, XML or Base64 format;
        levels: Levels part of the save (CCLocalLevels.dat). JSON, XML or Base64 format.
    Returns:
        200: Empty JSON;
        404: Failed to do a backup.
    Return Type:
        application/json
    """
    main = convert_to_encoded(request.query["main"])
    levels = convert_to_encoded(request.query["levels"])

    await request.app.client.backup(save_data=[main, levels])


@routes.delete("/api/comment/{id}")
@handle_errors(
    {
        KeyError: Error(400, "Parameter is missing.", ErrorType.MISSING_PARAMETER),
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to delete a comment.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def delete_comment(request: web.Request) -> web.Response:
    """DELETE /api/comment/{id}
    Description:
        Delete the profile comment, given by ID.
    Example:
        link: /api/comment/123456789
    Returns:
        200: Empty JSON;
        400: Parameter is missing;
        404: Failed to delete a comment.
    Return Type:
        application/json
    """
    comment_id = int(request.match_info["id"])

    await gd.Comment(type=gd.CommentType.PROFILE, id=comment_id, client=request.app.client).delete()

    return json_resp({})


@routes.delete("/api/level/{level_id}/comment/{comment_id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Failed to delete a comment.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def delete_level_comment(request: web.Request) -> web.Response:
    """DELETE /api/level/{level_id}/comment/{comment_id}
    Description:
        Delete the level (given by ID) comment, given by ID.
    Example:
        link: /api/level/1/comment/123456789
    Returns:
        200: Empty JSON;
        404: Failed to delete a comment.
    Return Type:
        application/json
    """
    level_id = int(request.match_info["level_id"])
    comment_id = int(request.match_info["comment_id"])

    await gd.Comment(
        type=gd.CommentType.LEVEL, id=comment_id, level_id=level_id, client=request.app.client
    ).delete()

    return json_resp({})


@routes.get("/api/ng/song/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Requested song not found.", ErrorType.NOT_FOUND),
    }
)
@auth_setup(required=False)
async def ng_song_search(request: web.Request) -> web.Response:
    """GET /api/ng/song/{id}
    Description:
        Fetch a song on Newgrounds by its ID.
    Example:
        link: /api/ng/song/1
    Returns:
        200: JSON with song info;
        400: Invalid type in payload;
        404: Song was not found.
    Return Type:
        application/json
    """
    query = int(request.match_info["id"])
    song = await request.app.client.get_ng_song(query)
    return json_resp(song)


@routes.get("/api/ng/users/{query}")
@handle_errors({ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE)})
@auth_setup(required=False)
async def ng_user_search(request: web.Request) -> web.Response:
    """GET /api/ng/users/{query}
    Description:
        Search for users on Newgrounds by given query.
    Example:
        link: /api/ng/users/Xtrullor?pages=0,1,2,3
        pages: 0,1,2,3
    Parameters:
        pages: Pages to load.
    Returns:
        200: JSON with user info;
        400: Invalid type in payload.
    Return Type:
        application/json
    """
    query = request.match_info["query"]
    pages = map(int, request.query.get("pages", "0").split(","))
    users = await request.app.client.search_users(query, pages=pages)
    return json_resp(users)


@routes.get("/api/ng/songs/{query}")
@handle_errors({ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE)})
@auth_setup(required=False)
async def ng_songs_search(request: web.Request) -> web.Response:
    """GET /api/ng/songs/{query}
    Description:
        Find songs on Newgrounds by given query.
    Example:
        link: /api/ng/songs/Panda Eyes?pages=0,1,2,3
        pages: 0,1,2,3
    Parameters:
        pages: Pages to load.
    Returns:
        200: JSON with user info;
        400: Invalid type in payload.
    Return Type:
        application/json
    """
    query = request.match_info["query"]
    pages = map(int, request.query.get("pages", "0").split(","))
    songs = await request.app.client.search_songs(query, pages=pages)
    return json_resp(songs)


@routes.get("/api/ng/user_songs/{user}")
@handle_errors()
@auth_setup(required=False)
async def search_songs_by_user(request: web.Request) -> web.Response:
    """GET /api/ng/user_songs/{user}
    Description:
        Find songs by given artist on Newgrounds.
    Example:
        link: /api/ng/user_songs/CreoMusic?pages=0,1,2,3
        pages: 0,1,2,3
    Parameters:
        pages: Pages to load.
    Returns:
        200: JSON with song info.
    Return Type:
        application/json
    """
    query = request.match_info["user"]
    pages = map(int, request.query.get("pages", "0").split(","))
    user_songs = await request.app.client.get_user_songs(query, pages=pages)
    return json_resp(user_songs)
'''
