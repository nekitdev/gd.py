"""API server implementation. Not to be confused with the HTTP requests implementation.
HTTP Request handler can be found at gd/utils/http_request.py.
"""

import functools
import platform
import re
import secrets

from aiohttp_cache import cache, setup_cache
from aiohttp import web
import aiohttp

from gd.typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Type, Union, ref
import gd

AUTH_RE = re.compile(r"(?:Token )?(?P<token>[A-Fa-z0-9]+)")
CLIENT = gd.Client()
JSON_PREFIX = "json_"

Function = Callable[[Any], Any]
Error = ref("gd.server.Error")

routes = web.RouteTableDef()


class ErrorType(gd.Enum):
    DEFAULT = 13000
    INVALID_TYPE = 13001
    MISSING_PARAMETER = 13002
    ACCESS_RESTRICTED = 13003
    NOT_FOUND = 13004
    FAILED = 13005
    LOGIN_FAILED = 13006
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
            "message": self.payload["data"]["message"].format(error=error),
            "error": type(error).__name__,
            "error_message": str(error),
        }
        self.payload["data"].update(to_add)
        return self

    def into_resp(self, **kwargs) -> web.Response:
        return json_resp(**self.payload, **kwargs)


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
        self.token = secrets.token_hex(64)

    def __repr__(self) -> str:
        info = {
            "token": self.token,
            "name": self.name,
            "account_id": self.account_id,
            "id": self.id,
        }
        return gd.utils.make_repr(self, info)

    def apply_to_client(self, client: gd.Client) -> None:
        client.edit(name=self.name, password=self.password, account_id=self.account_id, id=self.id)


class LoginManager:
    def __init__(self, client: gd.Client, info: TokenInfo) -> None:
        self.client = client
        self.info = info

    def __enter__(self) -> None:
        self.info.apply_to_client(self.client)

    def __exit__(self, *exc) -> None:
        self.client.close()


@web.middleware
async def auth_middleware(request: web.Request, handler: Function) -> web.Response:
    actual_handler = handler
    while isinstance(actual_handler, functools.partial):
        actual_handler = actual_handler.keywords.get("handler")

    if getattr(actual_handler, "needs_auth", False):
        auth = request.headers.get("Authorization")
        if auth is None:
            auth = request.query.get("token")
            if auth is None:
                return AUTH_NOT_SET.into_resp()

        match = AUTH_RE.match(auth)
        if match is None:
            return AUTH_INVALID.into_resp()

        token = match.group("token")

        info = gd.utils.get(request.app.tokens, token=token)
        if info is None:
            return AUTH_MISSING.into_resp()

        with LoginManager(request.app.client, info):
            return await handler(request)

    else:
        return await handler(request)


DEFAULT_MIDDLEWARES = [
    auth_middleware,
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

    setup_cache(app)

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


def needs_auth(required: bool) -> Function:
    def decorator(func: Function) -> Function:
        func.needs_auth = required
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


def parse_route_docs() -> Generator[Dict[str, Union[Dict[Union[str, int], str], str]], None, None]:
    for route in routes:
        info = dict(name=route.handler.__name__)
        info.update(parse_string(route.handler.__doc__))
        yield info


@routes.get("/api")
@handle_errors()
@needs_auth(False)
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
    print(await request.text())
    return json_resp(payload)


@routes.get("/api/auth")
@handle_errors(
    {
        KeyError: Error(400, "Parameter is missing.", ErrorType.MISSING_PARAMETER),
        gd.LoginFailure: Error(401, "Failed to login.", ErrorType.LOGIN_FAILED),
    }
)
@needs_auth(False)
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

    return json_resp({"token": token_info.token})


@routes.get("/api/user/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Requested user not found.", ErrorType.NOT_FOUND),
    }
)
@needs_auth(False)
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
    query = int(request.match_info.get("id"))
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
@needs_auth(False)
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
    query = int(request.match_info.get("id"))
    return json_resp(await request.app.client.get_song(query))


@routes.get("/api/search/user/{query}")
@handle_errors(
    {gd.MissingAccess: Error(404, "Requested user was not found.", ErrorType.NOT_FOUND),}
)
@needs_auth(False)
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
    query = request.match_info.get("query")
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
@needs_auth(False)
@cache(expires=10)
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
    level_id = int(request.match_info.get("id"))
    return json_resp(await request.app.client.get_level(level_id))


@routes.delete("/api/level/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "{error}", ErrorType.FAILED),
    }
)
@needs_auth(True)
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
    level_id = int(request.match_info.get("id"))
    level = await request.app.client.get_level(level_id, get_data=False)
    await level.delete()
    return json_resp({})


@routes.get("/api/install/{level_id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Requested level was not found.", ErrorType.NOT_FOUND),
    }
)
@needs_auth(False)
@cache(expires=10)
async def download_level(request: web.Request) -> web.Response:
    level_id = int(request.match_info.get("level_id"))
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
    {gd.MissingAccess: Error(404, "Daily is likely being refreshed.", ErrorType.NOT_FOUND),}
)
@needs_auth(False)
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
    return json_resp(await request.app.client.get_daily())


@routes.get("/api/weekly")
@handle_errors(
    {gd.MissingAccess: Error(404, "Weekly is likely being refreshed.", ErrorType.NOT_FOUND),}
)
@needs_auth(False)
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
    return json_resp(await request.app.client.get_weekly())


@routes.get("/api/messages")
@handle_errors(
    {gd.MissingAccess: Error(404, "Failed to load messages.", ErrorType.FAILED),}
)
@needs_auth(True)
@cache(expires=10)
async def get_messages(request: web.Request) -> web.Response:
    pages = map(int, request.query.get("pages", "0").split(","))
    sent = str_to_bool(request.query.get("sent", "false"))
    read = str_to_bool(request.query.get("read", "true"))
    sent_or_inbox = "sent" if sent else "inbox"

    messages = await request.app.client.get_messages(sent_or_inbox, pages=pages)

    if read:
        await gd.utils.gather(message.read() for message in messages)

    return json_resp(messages)


@routes.post("/api/send/{query}")
@handle_errors(
    {
        KeyError: Error(400, "Parameter is missing.", ErrorType.MISSING_PARAMETER),
        gd.MissingAccess: Error(404, "{error}", ErrorType.FAILED),
    }
)
@needs_auth(True)
async def send_message(request: web.Request) -> web.Response:
    query = request.match_info.get("query")

    is_id = str_to_bool(request.query.get("id", "false"))

    subject = request.query.get("subject", "No Subject")
    body = request.query["body"]

    if is_id:
        user = await request.app.client.fetch_user(int(query))
    else:
        user = await request.app.client.find_user(query)

    await user.send(subject, body)
    return json_resp({})


@routes.get("/api/ng/song/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE),
        gd.MissingAccess: Error(404, "Requested song not found.", ErrorType.NOT_FOUND),
    }
)
@needs_auth(False)
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
    query = int(request.match_info.get("id"))
    return json_resp(await request.app.client.get_song(query))


@routes.get("/api/ng/users/{query}")
@handle_errors({ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE)})
@needs_auth(False)
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
    query = request.match_info.get("query")
    pages = map(int, request.query.get("pages", "0").split(","))
    return json_resp(await request.app.client.search_users(query, pages=pages))


@routes.get("/api/ng/songs/{query}")
@handle_errors({ValueError: Error(400, "Invalid type in payload.", ErrorType.INVALID_TYPE)})
@needs_auth(False)
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
    query = request.match_info.get("query")
    pages = map(int, request.query.get("pages", "0").split(","))
    return json_resp(await request.app.client.search_songs(query, pages=pages))


@routes.get("/api/ng/user_songs/{user}")
@handle_errors()
@needs_auth(False)
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
    query = request.match_info.get("user")
    pages = map(int, request.query.get("pages", "0").split(","))
    return json_resp(await request.app.client.get_user_songs(query, pages=pages))
