import asyncio

import logging

from .utils.wrap_utils import _make_repr
from .utils.context import ctx
from .utils.http_request import http
from .classconverter import class_converter
from .utils.mapper import mapper_util
from .utils.errors import error
from .utils.gdpaginator import paginate
from .utils.routes import Route
from .utils.params import Parameters as Params
from .utils.indexer import Index as i
from .unreguser import UnregisteredUser
from .authclient import AuthClient

log = logging.getLogger(__name__)


class Client:
    def __init__(self):
        self._logged = False

    def __repr__(self):
        info = {
            'is_logged': self._logged
        }
        return _make_repr(self, info)

    def is_logged(self):
        return self._logged

    async def on_error(self, event_method, *args, **kwargs):
        print('Ignoring exception in {}'.format(event_method), file=sys.stderr)
        traceback.print_exc()

    async def get_song(self, songid: int = 0):
        if (songid == 0):
            raise error.IDNotSpecified('Song')
        parameters = Params().create_new().put_definer('song', str(songid)).finish()
        codes = {
            -1: MissingAccess(type='Song', id=songid),
            -2: SongRestrictedForUsage(songid)
        }
        resp = await http.fetch(Route.GET_SONG_INFO, parameters, splitter="~|~", error_codes=codes, should_map=True)
        return class_converter.SongConvert(resp)
    
    async def get_user(self, accountid: int = 0):
        if accountid == 0:
            raise error.IDNotSpecified('User')
        if accountid == -1:
            return UnregisteredUser()
        parameters = Params().create_new().put_definer('user', str(accountid)).finish()
        codes = {
            -1: MissingAccess(type='User', id=accountid)
        }
        resp = await http.fetch(Route.GET_USER_INFO, parameters, splitter=':', error_codes=codes, should_map=True)

        another = Params().create_new().put_definer('search', str(mapped.get(i.USER_PLAYER_ID))).put_page(0).finish()
        new_resp = http.send_request(Route.USER_SEARCH, another, splitter=':', error_codes=codes, should_map=True)
        new_dict = {
            i.USER_GLOW_OUTLINE: new_resp.get(i.USER_GLOW_OUTLINE),
            i.USER_ICON: new_resp.get(i.USER_ICON),
            i.USER_ICON_TYPE: new_resp.get(i.USER_ICON_TYPE)
        }
        for key in list(new_dict.keys()):
            mapped[key] = new_dict[key]
        return class_converter.UserConvert(mapped)
    
    async def login(self, user: str, password: str)
        parameters = Params().create_new().put_login_definer(username=user, password=password).finish_login()
        codes = {
            -1: FailedLogin(login=user, password=password)
        }
        resp = await http.fetch(Route.LOGIN, parameters, splitter=',', error_codes=codes)
        prepared = {
            'username': user, 'password': password,
            'account_id': int(resp[0]), 'id': int(resp[1])
        }
        for attr, value in prepared.items():
            ctx.upd(attr, value)
        log.info("Logged in as %s, with password %s", repr(user), repr(password))

    def event(self, coro):
        """A decorator that registers an event to listen to."""

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event registered must be a coroutine function.")

        setattr(self, coro.__name__, coro)
        log.debug("%s has been successfully registered as an event.", coro.__name__)

        return coro


# async def fetch(
#     route: str, parameters: dict = {}, 
#     splitter: str = None, error_codes: dict = {},  # error_codes is a dict: {code: error_to_raise}
#     should_map: bool = False  # whether response should be mapped 'enum -> value'
#     cookies: str = None, cookie: str = None
# ):
#     resp = await http.send_request(route, parameters, cookies, cookie)
#     if resp.error_code in error_codes:
#         raise error_codes.get(resp.error_code)
#     if splitter is not None:
#         resp = resp.split(splitter)
#     if should_map:
#         resp = mapper_util.map(resp)
#     return resp
#
#

# TO_DO: Make everything less messy...
