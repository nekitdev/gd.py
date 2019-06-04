from .utils.routes import Route
from .utils.params import Parameters as Params
from .utils.http_request import http
from .utils.errors import error
from .abstractentity import AbstractEntity

class Comment(AbstractEntity):
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
        
    def __str__(self):
        ret = f'[gd.Comment]\n[ID:{self.id}]\n[Rating:{self.rating}]\n[Timestamp:{self.timestamp}]\n[Body:{self.body}]\n[Author:{self.author.name}]'
        return ret

    @property
    def body(self):
        return self.options.get('body')
    @property
    def rating(self):
        return self.options.get('rating')
    @property
    def timestamp(self):
        return self.options.get('timestamp')
    @property
    def author(self):
        return self.options.get('author')
    @property
    def typeof(self):
        return self.options.get('type')
    @property
    def level_id(self):
        return self.options.get('level_id')
    @property
    def level_percentage(self):
        return self.options.get('level_percentage')

    def delete(self):
        from .authclient import AuthClient
        c = self.retrieved_from()
        if type(c) is not AuthClient:
            if c.attached() is None:
                raise error.InvalidArgument()
            else:
                c = c.attached()
        cases = {
            self.typeof is 0: Route.DELETE_LEVEL_COMMENT,
            self.typeof is 1: Route.DELETE_ACC_COMMENT
        }
        route = cases.get(True)
        config_type = 'client' if self.typeof is 1 else 'level'
        parameters = Params().create_new().put_definer('commentid', str(self.id)).put_definer('accountid', str(c.account_id)).put_password(c.encodedpass).comment_for(config_type, self.level_id).finish()
        resp = http.SendHTTPRequest(route, parameters)
        if resp is '1':
            return None
        raise error.MissingAccess()
    
    def retrieved_from(self):
        return self.options.get('retrieved_from')

    def is_disliked(self):
        return abs(self.rating) != self.rating