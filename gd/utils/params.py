from .errors import error

class Parameters:

    """Allows to build all parameters needed for HTTP requests,
    basically step-by-step, but huh... ._.')/"""

    def __init__(self):
        self.gameVersion = '21'
        self.binaryVersion = '35'
        self.secret = 'Wmfd2893gb7'
        self.login_secret = 'Wmfv3899gc9'
        self.dict = {}

    def create_new(self, type0: str = None):
        self.dict = {
            "gameVersion": self.gameVersion,
            "binaryVersion": self.binaryVersion,
            "gdw": "0"
        }
        return self
    
    def finish(self):
        self.dict["secret"] = self.secret
        return self.dict
    
    def finish_login(self):
        self.dict["secret"] = self.login_secret
        return self.dict
    
    def put_definer(self, for_what: str, item: str):
        for_what = for_what.lower()
        params_dict = {
            "song": "songID",
            "user": "targetAccountID",
            "search": "str",
            "leveldata": "levelID",
            "accountid": "accountID"
        }
        try:
            self.dict[params_dict[for_what]] = item
        except KeyError:
            raise error.InvalidArgument()
        return self
    
    def put_password(self, item: str):
        self.dict['gjp'] = item
        return self
        
    def put_type(self, number: int):
        self.dict['type'] = str(number)
        return self
    
    def put_page(self, number: int):
        self.dict['page'] = str(number)
        return self
    
    def put_total(self, number: int):
        self.dict['total'] = str(number)
        return self
        
    def put_login_definer(self, username: str, password: str):
        del self.dict["gdw"] # it is not needed in login request
        self.dict["udid"] = "Hello, Lord RubRub, it is a request from library [gd.py]"
        self.dict["userName"] = username
        self.dict["password"] = password
        return self
    
    def put_for_level(self, **kwargs):
        filters = kwargs.get('filters') #TO DO: work with filters to bring them cool look
        page = kwargs.get('page')
        none = self.check(filters)
        to_put = { #all filters will be passed through 'filters.py' formatter
            "len": "-" if none else filters.get('length'),
            "page": "0" if (page is None) else '{}'.format(page),
            "type": "0" if none else filters.get('type'),
            "diff": "-" if none else filters.get('difficulty'),
            "featured": "0" if none else filters.get('featured'),
            "original": "0" if none else filters.get('original'),
            "twoPlayer": "0" if none else filters.get('twoPlayer'),
            "coins": "0" if none else filters.get('coins'),
            "star": "0" if none else filters.get('starred')
        }
        if not none:
            if filters['noStar']:
                to_put["noStar"] = "1"
            if ('song' in list(filters.keys())):
                to_put["song"] = filters['song']
                to_put["customSong"] = filters['customSong']
            if ('demonFilter' in list(filters.keys())):
                to_put["demonFilter"] = filters['demonFilter']
            #TO DO: add 'completedLevels', 'followed', 'friends?' filters
        for key in list(to_put.keys()):
            self.dict[key] = to_put[key]
        return self
    
    def put_for_user(self, page: int = 0):
        self.dict["page"] = '{}'.format(page)
        return self

    def check(self, filters):
        if filters is None:
            return True
        else:
            return False
    
