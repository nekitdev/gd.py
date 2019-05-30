from .abstractentity import AbstractEntity
from .utils.http_request import http
from .utils.routes import Route
from .utils.indexer import Index as i
from .utils.mapper import mapper_util
from .utils.crypto.coders import Coder
from .utils.params import Parameters as Params
from .utils.errors import error
import base64

class Message(AbstractEntity):
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
        self._body = None
    
    def __str__(self):
        res = f'[gd.Message]\n[Author:{self.author.name}]\n[Recipient:{self.recipient.name}]\n[ID:{self.id}]\n[Subject:{self.subject}]\n[Body:{self.body}]\n[Is_Read:{self.is_read()}]\n[Type:{self.typeof.capitalize()}]\n[Timestamp:{self.timestamp}]'
        return res

    @property
    def author(self):
        return self.options.get('author')
    @property
    def recipient(self):
        return self.options.get('recipient')
    @property
    def subject(self):
        return self.options.get('subject')
    @property
    def timestamp(self):
        return self.options.get('timestamp')
    @property
    def typeof(self):
        return self.options.get('type')
    @property
    def body(self):
        return self._body
    
    def retrieved_from(self):
        return self.options.get('retrieved_from')

    def read(self):
        coder = Coder()
        c = self.retrieved_from()
        route = Route.READ_PRIVATE_MESSAGE
        params = Params().create_new().put_definer('accountid', str(c.account_id)).put_definer('messageid', str(self.id)).put_password(str(c.encodedpass)).put_is_sender(self.typeof).finish()
        resp = http.SendHTTPRequest(route, params)
        body = mapper_util.map(resp.split(':')).get(i.MESSAGE_BODY)
        ret = coder.decode0(type='message', string=mapper_util.normalize(body))
        self._body = ret
        return self.body

    def delete(self):
        c = self.retrieved_from()
        route = Route.DELETE_PRIVATE_MESSAGE
        params = Params().create_new().put_definer('accountid', str(c.account_id)).put_definer('messageid', str(self.id)).put_password(str(c.encodedpass)).put_is_sender(self.typeof).finish()
        resp = http.SendHTTPRequest(route, params)
        if resp is '1':
            return None
        else:
            raise error.MissingAccess()

    def is_read(self):
        return self.options.get('is_read')