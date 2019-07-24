from .utils.params import Parameters as Params
from .utils.http_request import http
from .utils.routes import Route
from .utils.mapper import mapper_util
from .utils.indexer import Index as i
# from .errors import error
from .utils.converter import Converter
from .utils.captcha_solver import Captcha
from .abstractentity import AbstractEntity
from .message import Message
from .abstractuser import AbstractUser
from .user import User
from .utils.gdpaginator import paginate as pagin
# like_item types: //to_be_implemented
# 1 - level
# 2 - level comment
# 3 - profile comment
class AuthClient(AbstractEntity):
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
        self._dict = {
            'name': options.get('name'),
            'id': options.get('id'),
            'account_id': options.get('accountid')
        }
        from .client import client
        self._as_user = client().get_user(options.get('accountid'), attached=self)

    def __str__(self):
        ret = f"[gd.AuthClient]\n[Name:{self.name}]\n[Password:{self.password}]\n[AccountID:{self.account_id}]\n[UserID:{self.id}]\n[Encoded_Password:{self.encodedpass}]"
        return ret
    
    def __repr__(self):
        ret = f"<gd.AuthClient: name={repr(self.name)}, password={repr(self.password)} id={self.id}, account_id={self.account_id}>"
        return ret

    @property
    def name(self):
        return self.options.get('name')
    @property
    def password(self):
        return self.options.get('password')
    @property
    def encodedpass(self):
        return self.options.get('encodedpass')
    @property
    def account_id(self):
        return self.options.get('accountid')

    def as_user(self):
        return self._as_user

    def req_mod(self):
        route = Route.REQUEST_MODERATOR
        params = Params().create_new().put_definer('accountid', str(self.account_id)).put_password(self.encodedpass).finish()
        resp = http.send_request(route, params)
        return int(resp)
    
    def get_friend_requests(self, sent_or_inbox: str = None, paginate = False, per_page = 10):
        from .classconverter import class_converter
        route = Route.GET_FRIEND_REQUESTS
        inbox = check_inbox(sent_or_inbox)
        params = Params().create_new().put_definer('accountid', str(self.account_id)).put_password(self.encodedpass).put_page(0).put_total(0).get_sent(inbox).finish()
        resp = http.send_request(route, params)
        final_res = []
        if resp == '-1':
            raise error.MissingAccess()
        if resp == '-2':
            raise error.NothingFound('friend_requests')
        else:
            to_map = resp.split('#')[0].split('|')
        for element in to_map:
            temp = element.split(':')
            to_put = ['TYPE', str(inbox)]; temp.extend(to_put)
            mapped = mapper_util.map(temp)
            final_res.append(class_converter.RequestConvert(mapped, self._dict, self))
        if not paginate:
            return final_res
        else:
            paginated = pagin(final_res, per_page=per_page)
            return paginated
    
    def get_friends(self, id_mode = False, paginate = False, per_page = 10):
        from .classconverter import class_converter
        route = Route.GET_FRIENDS
        parameters = Params().create_new().put_definer('accountid', str(self.account_id)).put_password(self.encodedpass).put_type(0).finish()
        ids, objects = [], []
        resp = http.send_request(route, parameters)
        if resp == '-1':
            raise error.MissingAccess()
        if resp == '-2':
            raise error.NothingFound('friends')
        else:
            to_map = resp.split('|')
            for element in to_map:
                temp = (mapper_util.map(element.split(':')))
                temp_accid = int(temp[i.USER_ACCOUNT_ID])
                temp_id = int(temp[i.USER_PLAYER_ID])
                temp_name = str(temp[i.USER_NAME])
                some_dict = {
                    'name': temp_name,
                    'id': temp_id,
                    'account_id': temp_accid
                }
                if id_mode:
                    ids.append(temp_accid)
                else:
                    converted = class_converter.AbstractUserConvert(some_dict)
                    objects.append(converted)
            if id_mode:
                return ids
            elif not paginate:
                return objects
            else:
                paginated = pagin(objects, per_page=per_page)
                return paginated

    def get_messages(self, sent_or_inbox: str = None, paginate = False, per_page = 10):
        from .classconverter import class_converter
        final_res = []
        inbox = check_inbox(sent_or_inbox)
        route = Route.GET_PRIVATE_MESSAGES
        parameters = Params().create_new().put_definer('accountid', str(self.account_id)).put_password(self.encodedpass).put_page(0).put_total(0).get_sent(inbox).finish()
        resp = http.send_request(route, parameters)
        if resp == '-1':
            raise error.MissingAccess()
        if resp == '-2':
            raise error.NothingFound('messages')
        else:
            to_map = resp.split('#')[0].split('|')
        for element in to_map:
            temp = element.split(':')
            mapped = mapper_util.map(temp)
            final_res.append(class_converter.MessageConvert(mapped, self._dict, self))
        if not paginate:
            return final_res
        else:
            paginated = pagin(final_res, per_page=per_page)
            return paginated
    
    def post_comment(self, content: str = None):
        if content is None:
            raise error.MissingArguments()
        else:
            route = Route.UPLOAD_ACC_COMMENT
            to_gen = [self.name, 0, 0, 1]
            parameters = Params().create_new().put_definer('accountid', str(self.account_id)).put_username(self.name).put_password(self.encodedpass).put_comment(content, to_gen).comment_for('client').finish()
            resp = http.send_request(route, parameters)
            if resp == '-1':
                raise error.MissingAccess()
            return self.get_comments()[0]
    
    def send_message(self, where = None, subject: str = None, body: str = None):
        if any(elem is None for elem in [where, subject, body]):
            raise error.MissingArguments()
        if type(where) in [AbstractUser, User]:
            recipient_id = where.account_id
        if type(where) is (int):
            recipient_id = where
        if type(where) is (str):
            from .client import client
            #where = client().search_users(name=where)[0]
            #recipient_id = where.account_id //I'll finish that soon...
            pass
        if type(where) not in [int, str, AbstractUser, User]:
            raise error.InvalidArgument()
        route = Route.SEND_PRIVATE_MESSAGE
        parameters = Params().create_new().put_definer('accountid', str(self.account_id)).put_message(subject, body).put_recipient(str(recipient_id)).put_password(str(self.encodedpass)).finish()
        resp = http.send_request(route, parameters)
        if resp == '-1':
            raise error.MissingAccess()
        if resp == '1':
            msg = self.get_messages('sent')[0]; msg.read()
            return msg
    
    def edit(self, name = None, password = None):
        if (password is None) and (name is None):
            raise error.MissingArguments()
        else:
            first_route = Route.MANAGE_ACCOUNT
            cookie = http.send_request(first_route, cookies='get')[1]
            second_route = Route.CAPTCHA
            captcha = http.send_request(second_route, cookies='add', cookie=cookie)
            number = Captcha().solve(captcha)
            params = Params().create_new('web').put_for_management(self.name, self.password, str(number)).close()
            http.send_request(first_route, params, cookies='add', cookie=cookie)
            if name is not None:
                route = Route.CHANGE_USERNAME
                test = http.send_request(route, cookies='add', cookie=cookie)
                if ('Username has already been changed once.' in test):
                    raise error.MissingAccess()
                else:
                    params = Params().create_new('web').put_for_username(self.name, name).close()
                    resp = http.send_request(route, params, cookies='add', cookie=cookie)
                    if ('Your username has been changed to' in resp):
                        print(f'Changed username to: {name}'); self.options["name"] = name
                    else:
                        raise error.MissingAccess()
            if password is not None:
                route = Route.CHANGE_PASSWORD
                http.send_request(route, cookies='add', cookie=cookie)
                params = Params().create_new('web').put_for_password(self.name, self.password, password).close()
                resp = http.send_request(route, params, cookies='add', cookie=cookie)
                if ('Password change failed' in resp):
                    raise error.MissingAccess()
                else:
                    print(f'Changed password to: {password}'); self.options["password"] = password
                    from .utils.crypto.coders import Coder
                    self.options["encodedpass"] = Coder().encode0(type='accountpass', string=self.password)

    def get_comments(self, pages = 1, paginate = False, per_page = 10):
        return self.as_user().get_comments(pages, paginate, per_page)
    
    def get_comment_history(self, pages = 1, paginate = False, per_page = 10):
        return self.as_user().get_comment_history(pages, paginate, per_page)

    def test_captcha(self): #It is just for testing
        route = Route.CAPTCHA; params = str()
        resp = http.send_request(route, params)
        c = Captcha(); res = c.solve(resp, with_image=True)
        return res

def check_inbox(sent_or_inbox):
    inbox = 0
    if (sent_or_inbox == 'sent'):
        inbox = 1
    if (sent_or_inbox is not None
    and sent_or_inbox != 'sent'):
        raise error.InvalidArgument()
    return inbox
