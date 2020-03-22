"""API server implementation. Not to be confused with the HTTP requests implementation.
HTTP Request handler can be found at gd/utils/http_requests.py.
"""

import functools
import platform
import re

from aiohttp import web
import aiohttp
from gd.typing import Any, Callable, Dict, Iterable, List, Optional, Type, ref
import gd

DEFAULT_MIDDLEWARES = [
    web.normalize_path_middleware(append_slash=False, remove_slash=True)
]
CLIENT = gd.Client()

Function = Callable[[Any], Any]
Error = ref('gd.server.Error')

routes = web.RouteTableDef()


class Error:
    def __init__(self, resp_code: int, message: str, **additional) -> None:
        self.data = {
            'status': resp_code,
            'data': {
                'message': message, 'exc': None, 'exc_message': None, **additional
            }
        }

    def set_error(self, exc: BaseException) -> Error:
        to_add = {
            'exc': type(exc).__name__,
            'exc_message': str(exc)
        }
        self.data.get('data').update(to_add)
        return self

    def into_resp(self, **kwargs) -> web.Response:
        return json_resp(**self.data, **kwargs)


DEFAULT_ERROR = Error(500, 'Server got into trouble.')


def json_dump(*args, **kwargs) -> str:
    kwargs.setdefault('indent', 4)
    return gd.utils.dump(*args, **kwargs)


def json_resp(*args, **kwargs) -> web.Response:
    func = json_dump if kwargs.pop('use_indent', True) else gd.utils.dump
    kwargs.setdefault('dumps', func)
    return web.json_response(*args, **kwargs)


def create_app(**kwargs) -> web.Application:
    kwargs.setdefault('middlewares', DEFAULT_MIDDLEWARES)
    app = web.Application(**kwargs)
    app.client = kwargs.get('client', CLIENT)
    app.add_routes(routes)
    return app


def run(app: web.Application, **kwargs) -> None:
    web.run_app(app, **kwargs)


def start(**kwargs) -> None:
    run(create_app(), **kwargs)


def handle_errors(error_dict: Dict[Type[BaseException], Error]) -> Function:
    def decorator(func: Function) -> Function:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> web.Response:
            try:
                return await func(*args, **kwargs)
            except BaseException as error:
                return error_dict.get(type(error), DEFAULT_ERROR).set_error(error).into_resp()
        return wrapper
    return decorator


def clean_str(string: str) -> str:
    return re.sub(r'\s+', ' ', string).strip()


def str_to_bool(
    string: str,
    true: Iterable[str] = {'yes', 'y', 'true', 't', '1', 'yeah', 'yep'},
    false: Iterable[str] = {'no', 'n', 'false', 'f', '0', 'nah', 'nope'}
) -> bool:  # I thought it might be cool ~ nekit
    string = string.casefold()
    if string in true:
        return True
    elif string in false:
        return False
    else:
        raise ValueError('Invalid string given: {!r}.'.format(string))


def parse_routes(routes: Iterable[web.RouteDef]) -> List[Dict[str, Optional[str]]]:
    def gen():
        for route in routes:
            yield {
                'name': route.handler.__name__,
                'description': clean_str(route.handler.__doc__),
                'path': route.path,
                'method': route.method
            }
    return list(gen())


@routes.get('/api')
async def main_page(request: web.Request) -> web.Response:
    """Return simple JSON with useful info.
    Returns:
        200 - JSON with API info.
    """
    payload = {
        'aiohttp': aiohttp.__version__,
        'gd.py': gd.__version__,
        'python': platform.python_version(),
        'routes': parse_routes(routes)
    }
    return json_resp(payload)


@routes.get('/api/user/{id}')
@handle_errors({
    ValueError: Error(400, 'Invalid type in payload.'),
    gd.MissingAccess: Error(404, 'Requested user not found.')
})
async def user_get(request: web.Request) -> web.Response:
    """Fetch a user by their Account ID.
    Returns:
        200 - JSON with user info;
        400 - Invalid type;
        404 - User was not found.
    """
    query = int(request.match_info.get('id'))
    return json_resp(await request.app.client.get_user(query))


@routes.get('/api/song/{id}')
@handle_errors({
    ValueError: Error(400, 'Invalid type in payload.'),
    gd.MissingAccess: Error(404, 'Requested song not found.'),
    gd.SongRestrictedForUsage: Error(403, 'Song is not allowed for use.')
})
async def song_search(request: web.Request) -> web.Response:
    """Fetch a song by its ID.
    Parameters:
        GET:
            ng - Bool indicating whether a song should be loaded from Newgrounds.
    Returns:
        200 - JSON with user info;
        400 - Invalid type in payload;
        403 - Song is not allowed to use;
        404 - Song was not found.
    """
    query = int(request.match_info.get('id'))
    is_ng = str_to_bool(request.rel_url.query.get('ng', 'false'))

    attr = ('get_ng_song' if is_ng else 'get_song')
    return json_resp(await getattr(request.app.client, attr)(query))


@routes.get('/api/search/user/{query}')
@handle_errors({
    gd.MissingAccess: Error(404, 'Requested user was not found.')
})
async def user_search(request: web.Request) -> web.Response:
    """Fetch a user by their name or player ID
    Returns:
        200 - JSON with user info;
        404 - User was not found.
    """
    query = request.match_info.get('query')
    return json_resp(await request.app.client.search_user(query))


@routes.get('/api/level/{id}')
@handle_errors({
    ValueError: Error(400, 'Invalid type in payload.'),
    gd.MissingAccess: Error(404, 'Requested level was not found')
})
async def get_level(request: web.Request) -> web.Response:
    """Fetch a level by given ID.
    Returns:
        200 - JSON with level info;
        400 - Invalid type;
        404 - Level was not found.
    """
    query = int(request.match_info.get('id'))
    return json_resp(await request.app.client.get_level(query, get_data=False))


@routes.get('/api/daily')
@handle_errors({
    gd.MissingAccess(404, 'Daily is likely being refreshed.')
})
async def get_daily(request: web.Request) -> web.Response:
    """Fetch current daily level.
    Returns:
        200 - JSON with daily info;
        404 - Daily is being refreshed.
    """
    return json_resp(await request.app.client.get_daily())


@routes.get('/api/weekly')
@handle_errors({
    gd.MissingAccess(404, 'Weekly is likely being refreshed.')
})
async def get_weekly(request: web.Request) -> web.Response:
    """Fetch current weekly level.
    Returns:
        200 - JSON with weekly info;
        404 - Weekly is being refreshed.
    """
    return json_resp(await request.app.client.get_weekly())
