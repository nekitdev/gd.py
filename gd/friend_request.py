from .abstractentity import AbstractEntity
from .utils.params import Parameters as Params
from .utils.routes import Route
from .utils.http_request import http
from .utils.errors import error

class FriendRequest(AbstractEntity):
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
        
    @property
    def author(self):
        return self.options.get('author')
    @property
    def recipient(self):
        return self.options.get('recipient')
    @property
    def typeof(self):
        return self.options.get('type')
    @property
    def body(self):
        return self.options.get('body')
    @property
    def timestamp(self):
        return self.options.get('timestamp')
    
    def is_read(self):
        return self.options.get('is_read')

    def retrieved_from(self):
        return self.options.get('retrieved_from')
    
    def delete(self):
        c = self.retrieved_from()
        user = self.author if self.typeof == 'normal' else self.recipient
        route = Route.DELETE_REQUEST
        params = Params().create_new().put_definer('accountid', str(c.account_id)).put_definer('user', str(user.account_id)).put_password(c.encodedpass).put_is_sender(self.typeof).finish()
        resp = http.SendHTTPRequest(route, params)
        if resp == '-1':
            raise error.MissingAccess()
        if resp == '1':
            return None

    def accept(self):
        c = self.retrieved_from()
        if self.typeof == 'sent':
            raise error.InvalidArgument()
        route = Route.ACCEPT_REQUEST
        params = Params().create_new().put_definer('accountid', str(c.account_id)).put_password(c.encodedpass).put_definer('user', str(self.author.account_id)).put_definer('requestid', str(self.id)).finish()
        resp = http.SendHTTPRequest(route, params)
        if resp == '-1':
            raise error.MissingAccess()
        if resp == '1':
            return None