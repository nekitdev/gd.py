"""API server implementation. Not to be confused with the HTTP requests implementation.
HTTP Request handler can be found at gd/utils/http_request.py.
"""

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

from gd.typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    ref,
)
import gd

AUTH_RE = re.compile(r"(?:Token )?(?P<token>[A-Fa-z0-9]+)")
CHUNK_SIZE = 64 * 1024
CLIENT = gd.Client()
JSON_PREFIX = "json_"

ROOT_PATH = Path(".gd")
if not ROOT_PATH.exists():
    ROOT_PATH.mkdir()

Function = Callable[[Any], Any]
Error = ref("gd.server.Error")
Cooldown = ref("gd.server.Cooldown")
CooldownMapping = ref("gd.server.CooldownMapping")

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
                "code_name": error_type.desc,
                "error": None,
                "error_message": None,
                **additional,
            },
        }

    def set_error(self, error: BaseException) -> Error:
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


DEFAULT_ERROR = Error(500, "Server got into trouble.", ErrorType.DEFAULT)
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

    def __exit__(self, *exc) -> None:
        self.client.close()


class Forward:
    def __init__(self, client: gd.Client, request: web.Request) -> None:
        self.http = client.http
        self.forwarded_for = request.remote
        self.backup = self.http.forwarded_for

    def __enter__(self) -> None:
        self.http.forwarded_for = self.forwarded_for

    def __exit__(self, *exc) -> None:
        self.http.forwarded_for = self.backup


@web.middleware
async def forward_middleware(request: web.Request, handler: Function) -> web.Response:
    with Forward(client=request.app.client, request=request):
        return await handler(request)


def get_original_handler(handler: Function) -> Function:
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
async def auth_middleware(request: web.Request, handler: Function) -> web.Response:
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

    def copy(self) -> Cooldown:
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

    def copy(self) -> CooldownMapping:
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
    def from_cooldown(cls, rate: int, per: float) -> CooldownMapping:
        return cls(Cooldown(rate, per))


def cooldown(rate: int, per: float) -> Function:
    def decorator(func: Function) -> Function:
        func.cooldown = CooldownMapping.from_cooldown(rate, per)
        return func

    return decorator


@web.middleware
async def rate_limit_middleware(request: web.Request, handler: Function) -> web.Response:
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
    forward_middleware,
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
    dumps = functools.partial(gd.utils.dump, **json_kwargs)
    actual_kwargs.setdefault("dumps", dumps)

    return web.json_response(*args, **actual_kwargs)


def create_app(**kwargs) -> web.Application:
    kwargs.update(middlewares=(kwargs.get("middlewares", []) + DEFAULT_MIDDLEWARES))

    app = web.Application(**kwargs)
    app.client = kwargs.get("client", CLIENT)
    app.tokens: List[TokenInfo] = []
    app.add_routes(routes)

    return app


def run(app: web.Application, **kwargs) -> None:
    web.run_app(app, **kwargs)


def start(**kwargs) -> None:
    run(create_app(), **kwargs)


def handle_errors(error_dict: Optional[Dict[Type[BaseException], Error]] = None) -> Function:
    if error_dict is None:
        error_dict = {}

    def decorator(func: Function) -> Function:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> web.Response:
            try:
                return await func(*args, **kwargs)
            except BaseException as error:
                return error_dict.get(type(error), DEFAULT_ERROR).set_error(error).into_resp()

        return wrapper

    return decorator


def auth_setup(required: bool = True) -> Function:
    def decorator(func: Function) -> Function:
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


def get_value(parameter: str, function: Function, default: Any, request: web.Request) -> Any:
    value = request.query.get(parameter)
    if value is None:
        value = default
    else:
        value = function(value)
    return value


def get_id_and_special(item_type: str, item_id: int = 0, level_id: int = 0) -> Optional[Tuple[int, int]]:
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
@auth_setup()
async def logout_handle(request: web.Request) -> web.Response:
    try:
        request.app.tokens.remove(request.token_info)
    except ValueError:
        pass  # nevermind

    return json_resp({})


@routes.get("/api/auth")
@handle_errors(
    {
        KeyError: Error(400, "Parameter is missing.", ErrorType.MISSING_PARAMETER),
        gd.LoginFailure: Error(401, "Failed to login.", ErrorType.LOGIN_FAILED),
    }
)
@auth_setup(required=False)
async def auth_handle(request: web.Request) -> web.Response:
    """GET /api/auth
    Description:
        Login into API system and get the token for further operation.
    Example:
        link: /api/auth?name=User&password=Password
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
        gd.SongRestrictedForUsage: Error(
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
    gauntlets = await request.app.client.get_gauntlets()
    return json_resp(gauntlets)


@routes.get("/api/map_packs")
@handle_errors({gd.MissingAccess: Error(404, "Failed to load map packs.", ErrorType.FAILED)})
@auth_setup(required=False)
async def get_map_packs(request: web.Request) -> web.Response:
    pages = map(int, request.query.get("pages", "0").split(","))
    map_packs = await request.app.client.get_map_packs(pages=pages)
    return json_resp(map_packs)


UPLOAD_QUERY: Dict[str, Tuple[Union[Callable[[str], Any], Any]]] = {
    "name": (str, "Unnamed"),
    "id": (int, 0),
    "version": (int, 1),
    "length": (
        functools.partial(string_to_enum, enum=gd.LevelLength),
        gd.LevelLength.TINY,
    ),
    "track": (int, 0),
    "song_id": (int, 0),
    "is_auto": (str_to_bool, False),
    "original": (int, 0),
    "two_player": (str_to_bool, False),
    "objects": (int, None),
    "coins": (int, 0),
    "star_amount": (int, 0),
    "unlist": (str_to_bool, False),
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
    upload_arguments = {
        parameter: get_value(parameter, function, default, request)
        for (parameter, (function, default)) in UPLOAD_QUERY.items()
    }

    level = await request.app.client.upload_level(**upload_arguments)

    return json_resp(level)


@routes.get("/api/levels")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get levels.", ErrorType.FAILED)})
@auth_setup(required=True)
async def get_levels(request: web.Request) -> web.Response:
    pages = map(int, request.query.get("pages", "0").split(","))
    levels = await request.app.client.get_levels(pages=pages)
    return json_resp(levels)


@routes.get("/api/messages")
@handle_errors({gd.MissingAccess: Error(404, "Failed to load messages.", ErrorType.FAILED)})
@auth_setup(required=True)
async def get_messages(request: web.Request) -> web.Response:
    pages = map(int, request.query.get("pages", "0").split(","))
    sent = str_to_bool(request.query.get("sent", "false"))
    read = str_to_bool(request.query.get("read", "true"))
    sent_or_inbox = "sent" if sent else "inbox"

    messages = await request.app.client.get_messages(sent_or_inbox, pages=pages)

    if read:
        await gd.utils.gather(message.read() for message in messages)

    return json_resp(messages)


@routes.get("/api/friend_requests")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get friend requests.", ErrorType.FAILED)})
@auth_setup(required=True)
async def get_friend_requests(request: web.Request) -> web.Response:
    pages = map(int, request.query.get("pages", "0").split(","))
    sent = str_to_bool(request.query.get("sent", "false"))
    read = str_to_bool(request.query.get("read", "false"))
    sent_or_inbox = "sent" if sent else "inbox"

    friend_requests = await request.app.client.get_friend_requests(sent_or_inbox, pages=pages)

    if read:
        await gd.utils.gather(friend_request.read() for friend_request in friend_requests)

    return json_resp(friend_requests)


@routes.get("/api/friend_request/{id}")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get a request.", ErrorType.FAILED)})
@auth_setup(required=True)
async def read_friend_request(request: web.Request) -> web.Response:
    request_id = int(request.match_info["id"])

    await gd.FriendRequest(id=request_id, client=request.app.client).read()

    return json_resp({})


@routes.delete("/api/friend_request/{id}")
@handle_errors({gd.MissingAccess: Error(404, "Failed to delete a request.", ErrorType.FAILED)})
@auth_setup(required=True)
async def delete_friend_request(request: web.Request) -> web.Response:
    request_id = int(request.match_info["id"])
    request_type = string_to_enum(request.query.get("type", "normal"), gd.MessageOrRequestType)
    account_id = int(request.query["author_id"])

    await gd.FriendRequest(
        author=gd.AbstractUser(account_id=account_id, client=request.app.client),
        id=request_id,
        type=request_type,
        client=request.app.client,
    ).delete()

    return json_resp({})


@routes.patch("/api/friend_request/{id}")
@handle_errors({gd.MissingAccess: Error(404, "Failed to accept a request.", ErrorType.FAILED)})
@auth_setup(required=True)
async def accept_friend_request(request: web.Request) -> web.Response:
    request_id = int(request.match_info["id"])
    request_type = string_to_enum(request.query.get("type", "normal"), gd.MessageOrRequestType)
    account_id = int(request.query["author_id"])

    await gd.FriendRequest(
        author=gd.AbstractUser(account_id=account_id, client=request.app.client),
        id=request_id,
        type=request_type,
        client=request.app.client,
    ).accept()

    return json_resp({})


@routes.get("/api/friends")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get friends.", ErrorType.FAILED)})
@auth_setup(required=True)
async def get_friends(request: web.Request) -> web.Response:
    friends = await request.app.client.get_friends()
    return json_resp(friends)


@routes.patch("/api/{action:(unblock|block)}/{id}")
@handle_errors({gd.MissingAccess: Error(404, "Failed to (un)block user.", ErrorType.FAILED)})
@auth_setup(required=True)
async def un_block_user(request: web.Request) -> web.Response:
    account_id = int(request.match_info["id"])
    unblock = request.match_info["action"].startswith("un")

    user = await gd.AbstractUser(account_id=account_id, client=request.app.client)

    if unblock:
        await user.unblock()
    else:
        await user.block()

    return json_resp({})


@routes.patch("/api/{action:(unfriend|friend)}/{id}")
@handle_errors({gd.MissingAccess: Error(404, "Failed to (un)friend user.", ErrorType.FAILED)})
@auth_setup(required=True)
async def un_friend_user(request: web.Request) -> web.Response:
    account_id = int(request.match_info["id"])
    unfriend = request.match_info["action"].startswith("un")
    message = request.query.get("message", "")

    user = gd.AbstractUser(account_id=account_id, client=request.app.client)

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
    blocked = await request.app.client.get_blocked_users()
    return json_resp(blocked)


@routes.post("/api/send/{query}")
@handle_errors(
    {
        KeyError: Error(400, "Parameter is missing.", ErrorType.MISSING_PARAMETER),
        gd.MissingAccess: Error(404, "{error}", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
@cooldown(rate=5, per=5)
async def send_message(request: web.Request) -> web.Response:
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
        gd.MissingAccess: Error(404, "Failed to like an entity.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
@cooldown(rate=5, per=5)
async def like_item(request: web.Request) -> web.Response:
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
@handle_errors({gd.MissingAccess: Error(404, "Failed to rate a level.", ErrorType.FAILED)})
@auth_setup(required=True)
@cooldown(rate=5, per=5)
async def rate_level(request: web.Request) -> web.Response:
    level_id = int(request.match_info["id"])
    stars = int(request.query["stars"])

    await gd.Level(id=level_id, client=request.app.client).rate(stars)
    return json_resp({})


@routes.patch("/api/level/{id}/description")
@handle_errors(
    {gd.MissingAccess: Error(404, "Failed to update level description.", ErrorType.FAILED)}
)
@auth_setup(required=True)
async def update_level_description(request: web.Request) -> web.Response:
    level_id = int(request.match_info["id"])
    new = request.query["new"]

    await gd.Level(id=level_id, client=request.app.client).update_description(new)
    return json_resp({})


@routes.patch("/api/level/{id}/rate_demon")
@handle_errors({gd.MissingAccess: Error(404, "Failed to demon-rate a level.", ErrorType.FAILED)})
@auth_setup(required=True)
async def rate_level_demon(request: web.Request) -> web.Response:
    level_id = int(request.match_info["id"])
    demon_difficulty = string_to_enum(request.query["difficulty"], gd.DemonDifficulty)
    as_mod = str_to_bool(request.query.get("mod", "false"))

    await gd.Level(
        id=level_id, client=request.app.client
    ).rate_demon(demon_difficulty, as_mod=as_mod)

    return json_resp({})


@routes.patch("/api/level/{id}/send")
@handle_errors({gd.MissingAccess: Error(404, "Failed to send a level.", ErrorType.FAILED)})
@auth_setup(required=True)
async def send_level(request: web.Request) -> web.Response:
    level_id = int(request.match_info["id"])
    stars = int(request.query["stars"])
    featured = str_to_bool(request.query["featured"])

    await gd.Level(id=level_id, client=request.app.client).send(stars, featured=featured)

    return json_resp({})


@routes.get("/api/level/{id}/comments")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get level comments.", ErrorType.FAILED)})
@auth_setup(required=False)
async def get_level_comments(request: web.Request) -> web.Response:
    level_id = int(request.match_info["id"])
    amount = int(request.query.get("amount", 20))
    strategy = string_to_enum(request.query.get("strategy", "recent"), gd.CommentStrategy)

    comments = await gd.Level(
        id=level_id, client=request.app.client
    ).get_comments(amount=amount, strategy=strategy)

    return json_resp(comments)


@routes.get("/api/level/{id}/leaderboard")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get the leaderboard.", ErrorType.FAILED)})
@auth_setup(required=True)
async def get_level_leaderboard(request: web.Request) -> web.Response:
    level_id = int(request.match_info["id"])
    strategy = string_to_enum(
        request.match_info.get("strategy", "all"), gd.LevelLeaderboardStrategy
    )

    records = await gd.Level(
        id=level_id, client=request.app.client
    ).get_leaderboard(strategy=strategy)

    return json_resp(records)


@routes.get("/api/user/{id}/comments")
@handle_errors({gd.MissingAccess: Error(404, "Failed to get user comments.", ErrorType.FAILED)})
@auth_setup(required=False)
async def get_user_comments(request: web.Request) -> web.Response:
    account_id = int(request.match_info["id"])
    pages = map(int, request.query.get("pages", "0").split(","))
    type_str = request.query.get("type", "profile")
    strategy = string_to_enum(request.query.get("strategy", "recent"), gd.CommentStrategy)

    user = await request.app.client.fetch_user(account_id)
    comments = await user.retrieve_comments(type=type_str, pages=pages, strategy=strategy)

    return json_resp(comments)


@routes.post("/api/comment/{level_id}")
@handle_errors({gd.MissingAccess: Error(404, "Failed to comment a level.", ErrorType.FAILED)})
@auth_setup(required=True)
async def comment_level(request: web.Request) -> web.Response:
    level_id = int(request.match_info["level_id"])
    body = request.query["body"]
    percentage = int(request.query.get("percentage", 0))

    await gd.Level(id=level_id, client=request.app.client).comment(body, percentage)

    return json_resp({})


@routes.post("/api/comment")
@handle_errors({gd.MissingAccess: Error(404, "Failed to post a comment.", ErrorType.FAILED)})
@auth_setup(required=True)
async def post_comment(request: web.Request) -> web.Response:
    body = request.query["body"]

    await request.app.client.post_comment(body)

    return json_resp({})


SETTINGS_QUERY: Dict[str, Tuple[Union[Callable[[str], Any], Any]]] = {
    "message_policy": (
        functools.partial(string_to_enum, enum=gd.MessagePolicyType), None
    ),
    "friend_request_policy": (
        functools.partial(string_to_enum, enum=gd.FriendRequestPolicyType), None
    ),
    "comment_policy": (
        functools.partial(string_to_enum, enum=gd.CommentPolicyType), None
    ),
    "youtube": (str, None),
    "twitter": (str, None),
    "twitch": (str, None),
}


PROFILE_QUERY: Dict[str, Tuple[Union[Callable[[str], Any], Any]]] = {
    "stars": (int, None),
    "demons": (int, None),
    "diamonds": (int, None),
    "has_glow": (bool, None),
    "icon_type": (
        functools.partial(string_to_enum, enum=gd.IconType), None
    ),
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


@routes.patch("/api/settings")
@handle_errors({gd.MissingAccess: Error(404, "Failed to edit settings.", ErrorType.FAILED)})
@auth_setup(required=True)
async def update_settings(request: web.Request) -> web.Response:
    update_arguments = {
        parameter: get_value(parameter, function, default, request)
        for (parameter, (function, default)) in SETTINGS_QUERY.items()
    }

    await request.app.client.update_settings(**update_arguments)

    return json_resp({})


@routes.patch("/api/profile")
@handle_errors({gd.MissingAccess: Error(404, "Failed to update profile.", ErrorType.FAILED)})
@auth_setup(required=True)
async def update_profile(request: web.Request) -> web.Response:
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


@routes.get("/api/icons/{type:(all|main|cube|ship|ball|ufo|wave|robot|spider)}/{query}")
@handle_errors(
    {gd.MissingAccess: Error(404, "Could not find requested user.", ErrorType.NOT_FOUND)}
)
@auth_setup(required=False)
async def get_icons(request: web.Request) -> web.Response:
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

    request.loop.create_task(delete_after(5, path))

    return web.FileResponse(path)


@routes.get("/api/search/levels")
@handle_errors()
@auth_setup(required=False)
async def search_levels(request: web.Request) -> web.Response:
    return json_resp([])  # TODO: finish this one

    levels = await request.app.client.search_levels(...)

    return json_resp(levels)


@routes.get("/api/load")
@handle_errors({gd.MissingAccess: Error(404, "Failed to load the save.", ErrorType.FAILED)})
@auth_setup(required=True)
@cooldown(rate=10, per=50)
async def load_save(request: web.Request) -> web.Response:
    await request.app.client.load()
    return json_resp(request.app.client.db)


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
@cooldown(rate=10, per=50)
async def backup_save(request: web.Request) -> web.Response:
    main = convert_to_encoded(request.query["main"])
    levels = convert_to_encoded(request.query["levels"])
    return print(main, levels)

    await request.app.client.backup(save_data=[main, levels])


@routes.delete("/api/comment/{id}")
@handle_errors(
    {
        KeyError: Error(400, "Parameter is missing.", ErrorType.MISSING_PARAMETER),
        gd.MissingAccess: Error(404, "Failed to delete a comment.", ErrorType.FAILED),
    }
)
@auth_setup(required=True)
async def delete_comment(request: web.Request) -> web.Response:
    comment_id = int(request.match_info["id"])
    comment_type = string_to_enum(request.query["type"], gd.CommentType)
    level_id = int(request.query.get("level_id", 0))

    await gd.Comment(
        type=comment_type, id=comment_id, level_id=level_id, client=request.app.client
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
