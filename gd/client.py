import asyncio

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
#initializing other things here
class client:
    def __repr__(self):
        ret = '<gd.client>'
        return ret

    def __init__(self):
        self.error_code = '-1'

    def event(self, coro):
        """A decorator that registers an event to listen to."""

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event registered must be a coroutine function.")

        setattr(self, coro.__name__, coro)
        # log here
        return coro

    def get_song(self, songid: int = 0):
        if (songid == 0):
            raise error.IDNotSpecified('Song')
        else:
            parameters = Params().create_new().put_definer('song', str(songid)).finish()
            resp = http.send_request(Route.GET_SONG_INFO, parameters)
            if resp == self.error_code:
                raise error.MissingAccess(type='Song', id=songid)
            if resp == '-2':
                raise error.SongRestrictedForUsage(songid) 
            else:
                resp = resp.split("~|~")
                mapped = mapper_util.map(resp)
                song = class_converter.SongConvert(mapped)
                return song
    
    def get_user(self, accountid: int = None, attached: AuthClient = None):
        if accountid is None:
            raise error.MissingArguments()
        if accountid is 0:
            return UnregisteredUser()
        else:
            parameters = Params().create_new().put_definer('user', str(accountid)).finish()
            resp = http.send_request(Route.GET_USER_INFO, parameters)
            if resp == self.error_code:
                raise error.MissingAccess(type='User', id=accountid)
            resp = resp.split(':')
            mapped = mapper_util.map(resp)
            another_params = Params().create_new().put_definer('search', str(mapped[i.USER_PLAYER_ID])).put_page(0).finish()
            new_resp = http.send_request(Route.USER_SEARCH, another_params)
            new_resp = mapper_util.map(new_resp.split(':'))
            new_dict = {
                i.USER_GLOW_OUTLINE: new_resp[i.USER_GLOW_OUTLINE],
                i.USER_ICON: new_resp[i.USER_ICON],
                i.USER_ICON_TYPE: new_resp[i.USER_ICON_TYPE]
            }
            for key in list(new_dict.keys()):
                mapped[key] = new_dict[key]
            user = class_converter.UserConvert(mapped)
            if attached is not None:
                user.options["attached"] = attached
            return user
    
    def get_level(self, levelid: int = 0):
        if levelid == 0:
            raise error.IDNotSpecified('Level')
        else:
            to_map = []
            parameters = Params().create_new().put_definer('search', str(levelid)).put_for_level().finish()
            resp = http.send_request(Route.LEVEL_SEARCH, parameters)
            if resp == self.error_code:
                self.emit_counter()
                raise error.NothingFound('levels')
            resp = resp.split('#')
            levelinfo = resp[0].split(':')
            creatorinfo = mapper_util.map(
                resp[1].split(':')
            ) if (len(resp[1]) > 0) else UnregisteredUser()
            songinfo = mapper_util.map(
                resp[2].split('~|~')
            ) if (len(resp[2]) > 0) else ('Normal Song')
            data = Params().create_new().put_definer('leveldata', str(levelid)).finish()
            lvldata = http.send_request(Route.DOWNLOAD_LEVEL, data)
            lvldata = lvldata.split(':')
            mapped1 = mapper_util.map(lvldata)
            mapped2 = mapper_util.map(levelinfo)
            creator = class_converter.AbstractUserConvert(
                creatorinfo
            ) if type(creatorinfo) is dict else creatorinfo
            print(f'{resp}\n{levelinfo}\n{songinfo}\n{creatorinfo}\n{lvldata}') #THIS IS NOT READY AT ALL
            #level = class_converter.LevelConvert(mapped)
    
    def login(self, user: str = None, password: str = None):
        if (password is None) or (user is None):
            raise error.MissingArguments()
        else:
            parameters = Params().create_new().put_login_definer(username=user, password=password).finish_login()
            resp = http.send_request(Route.LOGIN, parameters)
            if resp == self.error_code:
                raise error.FailedLogin(login=user, password=password)
            else:
                resp = resp.split(',')
                to_convert = {'username': user, 'password': password, 'accountid': resp[0], 'userid': resp[1]}
                authclient = class_converter.AuthClientConvert(to_convert)
                return authclient


# async def fetch(
#     route: str, parameters: dict = {}, 
#     splitter: str = None, error_codes: dict = [],  # error_codes is a dict: {code: error_to_raise}
#     cookies: str = None, cookie: str = None
# ):
#     resp = await http.send_request(route, parameters, cookies, cookie)
#     if resp.error_code in error_codes:
#         raise error_codes.get(resp.error_code)
#     if splitter is not None:
#         resp = resp.split(splitter)
#     return resp
#
#

# TO_DO: Make everything less messy...
