from .mapper import mapper_util
from .crypto.coders import Coder
import base64
import random

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
        if type0 is None:
            self.dict = {
                "gameVersion": self.gameVersion,
                "binaryVersion": self.binaryVersion,
                "gdw": "0"
            }
        if type0 == 'web':
            self.dict = {}
        return self
    
    def finish(self):
        self.dict["secret"] = self.secret
        return self.dict
    
    def finish_login(self):
        self.dict["secret"] = self.login_secret
        return self.dict
    
    def close(self):
        return self.dict
    
    def put_for_management(self, login, password, code):
        to_put = {
            'username': login,
            'password': password,
            'vercode': code,
            'cmdlogin': 'Login'
        }
        for key in list(to_put.keys()):
            self.dict[key] = to_put[key]
        return self
    
    def put_for_username(self, name, newname):
        to_put = {
            "username": name,
            "newusername": newname,
            "changeusername": 'Change Username'
        }
        for key in list(to_put.keys()):
            self.dict[key] = to_put[key]
        return self
    
    def put_for_password(self, name, password, newpass):
        to_put = {
            "username": name,
            "oldpassword": password,
            "password": newpass,
            "password2": newpass,
            "change": 'Change Password'
        }
        for key in list(to_put.keys()):
            self.dict[key] = to_put[key]
        return self        

    def put_definer(self, for_what: str, item: str):
        for_what = for_what.lower()
        params_dict = {
            "song": "songID",
            "user": "targetAccountID",
            "search": "str",
            "leveldata": "levelID",
            "accountid": "accountID",
            "messageid": "messageID",
            "commentid": "commentID",
            "requestid": "requestID",
            "userid": "userID"
        }
        try:
            self.dict[params_dict[for_what]] = item
        except KeyError:
            pass
        return self
    
    def put_recipient(self, account_id:str):
        self.dict['toAccountID'] = account_id
        return self
        
    def put_is_sender(self, t: str):
        if t is 'normal':
            pass
        if t is 'sent':
            self.dict['isSender'] = "1"
        return self
    
    def put_message(self, subject:str, body:str):
        self.dict['subject'] = base64.b64encode(subject.encode()).decode()
        self.dict['body'] = mapper_util.prepare_sending(Coder().encode0(type='message', string=body))
        return self

    def put_password(self, item: str):
        self.dict['gjp'] = item
        return self
    
    def put_username(self, item: str):
        self.dict['userName'] = item
        return self
        
    def put_type(self, number: int):
        self.dict['type'] = str(number)
        return self
    
    def put_page(self, number: int):
        self.dict['page'] = str(number)
        return self
    
    def put_comment(self, content: str, values: list):
        comment = mapper_util.prepare_sending(base64.b64encode(content.encode()).decode())
        self.dict['comment'] = comment
        values.insert(1, comment)
        self.dict['chk'] = Coder().gen_chk(type='comment', values=values)
        return self
    
    def comment_for(self, type0: str, number: int = None):
        if type0 in ('client', 'level'):
            if (type0 == 'client'):
                self.dict['cType'] = "1"
            else:
                self.dict['levelID'] = str(number)
        return self

    def put_total(self, number: int):
        self.dict['total'] = str(number)
        return self
    
    def put_mode(self, number: int):
        self.dict['mode'] = str(number)
        return self
        
    def put_login_definer(self, username: str, password: str):
        del self.dict["gdw"] # it is not needed in login request
        self.dict["udid"] = f"[{random.randint(100000, 999999)}][gd.py]" # for fun
        self.dict["password"] = password
        self.put_username(username)
        return self
    
    def put_for_level(self, **kwargs):
        filters = kwargs.get('filters') #TO DO: work with filters to bring them cool look
        page = kwargs.get('page')
        none = self.check(filters)
        to_put = { #all filters will be passed through 'filters.py' formatter
            "len": "-" if none else filters.get('length'),
            "page": "0" if (page is None) else str(page),
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
    
    def get_sent(self, indicator: int):
        if (indicator==1):
            self.dict["getSent"] = '1'
        else:
            pass
        return self

    def check(self, filters):
        if filters is None:
            return True
        else:
            return False