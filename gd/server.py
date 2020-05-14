"""API server implementation. Not to be confused with the HTTP requests implementation.
HTTP Request handler can be found at gd/utils/http_request.py.
"""

import functools
import platform

from aiohttp import web
import aiohttp
from gd.typing import Any, Callable, Dict, Generator, Iterable, Optional, Type, Union, ref
import gd

DEFAULT_MIDDLEWARES = [web.normalize_path_middleware(append_slash=False, remove_slash=True)]
CLIENT = gd.Client()

Function = Callable[[Any], Any]
Error = ref("gd.server.Error")

routes = web.RouteTableDef()


class Error:
    def __init__(self, resp_code: int, message: str, **additional) -> None:
        self.data = {
            "status": resp_code,
            "data": {"message": message, "exc": None, "exc_message": None, **additional},
        }

    def set_error(self, exc: BaseException) -> Error:
        to_add = {"exc": type(exc).__name__, "exc_message": str(exc)}
        self.data.get("data").update(to_add)
        return self

    def into_resp(self, **kwargs) -> web.Response:
        return json_resp(**self.data, **kwargs)


DEFAULT_ERROR = Error(500, "Server got into trouble.")


def parse_string(string: str) -> Dict[str, Union[Dict[Union[str, int], str], str]]:
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


def json_dump(*args, **kwargs) -> str:
    kwargs.setdefault("indent", 4)
    return gd.utils.dump(*args, **kwargs)


def json_resp(*args, **kwargs) -> web.Response:
    func = json_dump if kwargs.pop("use_indent", True) else gd.utils.dump
    kwargs.setdefault("dumps", func)
    return web.json_response(*args, **kwargs)


def create_app(**kwargs) -> web.Application:
    kwargs.setdefault("middlewares", DEFAULT_MIDDLEWARES)
    app = web.Application(**kwargs)
    app.client = kwargs.get("client", CLIENT)
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


def str_to_bool(
    string: str,
    true: Iterable[str] = {"yes", "y", "true", "t", "1", "yeah", "yep"},
    false: Iterable[str] = {"no", "n", "false", "f", "0", "nah", "nope"},
) -> bool:  # I thought it might be cool ~ nekit
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


@routes.get("/api/user/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload."),
        gd.MissingAccess: Error(404, "Requested user not found."),
    }
)
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
    return json_resp(await request.app.client.get_user(query))


@routes.get("/api/song/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload."),
        gd.MissingAccess: Error(404, "Requested song not found."),
        gd.SongRestrictedForUsage: Error(403, "Song is not allowed for use."),
    }
)
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
@handle_errors({gd.MissingAccess: Error(404, "Requested user was not found.")})
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
    return json_resp(await request.app.client.search_user(query))


@routes.get("/api/level/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload."),
        gd.MissingAccess: Error(404, "Requested level was not found"),
    }
)
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
    query = int(request.match_info.get("id"))
    return json_resp(await request.app.client.get_level(query))


@routes.get("/api/daily")
@handle_errors({gd.MissingAccess: Error(404, "Daily is likely being refreshed.")})
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
@handle_errors({gd.MissingAccess: Error(404, "Weekly is likely being refreshed.")})
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


@routes.get("/api/ng/song/{id}")
@handle_errors(
    {
        ValueError: Error(400, "Invalid type in payload."),
        gd.MissingAccess: Error(404, "Requested song not found."),
    }
)
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
@handle_errors({ValueError: Error(400, "Invalid type in payload.")})
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
    pages = map(int, request.rel_url.query.get("pages", "0").split(","))
    return json_resp(await request.app.client.search_users(query, pages=pages))


@routes.get("/api/ng/songs/{query}")
@handle_errors({ValueError: Error(400, "Invalid type in payload.")})
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
    pages = map(int, request.rel_url.query.get("pages", "0").split(","))
    return json_resp(await request.app.client.search_songs(query, pages=pages))


@routes.get("/api/ng/user_songs/{user}")
@handle_errors()
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
    pages = map(int, request.rel_url.query.get("pages", "0").split(","))
    return json_resp(await request.app.client.get_user_songs(query, pages=pages))
