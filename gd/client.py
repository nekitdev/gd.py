from .utils.http_request import http
from .classconverter import class_converter
from .utils.mapper import mapper_util
from .utils.errors import error
from .utils.gdpaginator import paginate
from .utils.routes import Route
from .utils.params import Parameters as Params
from .utils.indexer import Index as i
#initializing other things here
class client:
    def __init__(self):
        self.error_code = '-1'

    def get_song(self, songid: int = 0):
        if (songid == 0):
            raise error.IDNotSpecified('Song')
        else:
            parameters = Params().create_new().put_definer('song', str(songid)).finish()
            resp = http.SendHTTPRequest(Route.GET_SONG_INFO, parameters)
            if resp == self.error_code:
                raise error.MissingAccess(type='Song', id=songid)
            if resp == '-2':
                raise error.SongRestrictedForUsage(songid) 
            else:
                resp = resp.split("~|~")
                mapped = mapper_util.map(resp)
                song = class_converter.SongConvert(mapped)
                return song
    
    def get_user(self, accountid: int = 0):
        if accountid == 0:
            raise error.IDNotSpecified('User')
        else:
            parameters = Params().create_new().put_definer('user', str(accountid)).finish()
            resp = http.SendHTTPRequest(Route.GET_USER_INFO, parameters)
            if resp == self.error_code:          
                raise error.MissingAccess(type='User', id=accountid)
            resp = resp.split(':')
            mapped = mapper_util.map(resp)
            another_params = Params().create_new().put_definer('search', str(mapped[i.USER_PLAYER_ID])).put_page(0).finish()
            new_resp = http.SendHTTPRequest(Route.USER_SEARCH, another_params)
            new_resp = mapper_util.map(new_resp.split(':'))
            new_dict = {
                i.USER_GLOW_OUTLINE: new_resp[i.USER_GLOW_OUTLINE],
                i.USER_ICON: new_resp[i.USER_ICON],
                i.USER_ICON_TYPE: new_resp[i.USER_ICON_TYPE]
            }
            for key in list(new_dict.keys()):
                mapped[key] = new_dict[key]
            user = class_converter.UserConvert(mapped)
            return user
    
    def get_level(self, levelid: int = 0):
        if levelid == 0:
            raise error.IDNotSpecified('Level')
        else:
            to_map = []
            parameters = Params().create_new().put_definer('search', str(levelid)).finish()
            resp = http.SendHTTPRequest(Route.LEVEL_SEARCH, parameters)
            resp = resp.split('#')
            levelinfo = resp[0].split()[0]
            creatorinfo = resp[1].split()[0]
            songinfo = resp[2].split()[0]
            to_map.extend([levelinfo, creatorinfo, songinfo])
            data = Params().create_new().put_definer('leveldata', str(levelid)).finish()
            lvldata = http.SendHTTPRequest(Route.DOWNLOAD_LEVEL, data)
            lvldata = lvldata.split()
            to_map.append(lvldata)
            mapped = {}
            for item in to_map:
                temp = mapper_util.map(item)
                for key in temp:
                    mapped[key] = temp[key]
            level = class_converter.LevelConvert(mapped)
            return "Not finished yet, still in progress..."
            #work with those in 'gd.Level' object
    
    def login(self, **options):
        if len(options) > 2:
            raise error.TooManyArguments()
        password = options.get('password')
        login = options.get('user')
        if (password is None) or (login is None):
            raise error.MissingArguments()
        else:
            parameters = Params().create_new().put_login_definer(username=login, password=password).finish_login()
            resp = http.SendHTTPRequest(Route.LOGIN, parameters)
            if resp == self.error_code:
                raise error.FailedLogin(login=login, password=password)
            else:
                resp = resp.split(',')
                to_convert = {'username': login, 'password': password, 'accountid': resp[0], 'userid': resp[1]}
                authclient = class_converter.AuthClientConvert(to_convert)
                return authclient
            
