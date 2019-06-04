from .utils.errors import error
from .utils.http_request import http
from .utils.routes import Route
from .utils.params import Parameters as Params
from .utils.mapper import mapper_util
from .utils.gdpaginator import paginate as pagin
from .abstractentity import AbstractEntity

class User(AbstractEntity):
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options

    @property
    def name(self):
        return self.options.get('name')
    @property
    def account_id(self):
        return self.options.get('account_id')
    @property
    def stars(self):
        return self.options.get('stars')
    @property
    def demons(self):
        return self.options.get('demons')
    @property
    def cp(self):
        return self.options.get('cp')
    @property
    def diamonds(self):
        return self.options.get('diamonds')
    @property
    def role(self):
        return self.options.get('role')
    @property
    def rank(self):
        return self.options.get('global_rank')
    @property
    def youtube(self):
        return self.options.get('youtube')
    @property
    def twitter(self):
        return self.options.get('twitter')[0]
    @property
    def twitter_link(self):
        return self.options.get('twitter')[1]
    @property
    def twitch(self):
        return self.options.get('twitch')[0]
    @property
    def twitch_link(self):
        return self.options.get('twitch')[1]
    @property
    def msg_policy(self):
        return self.options.get('messages')
    @property
    def friend_req_policy(self):
        return self.options.get('friend_requests')
    @property
    def comments_policy(self):
        return self.options.get('comments')
    @property
    def icon_set(self):
        return self.options.get('icon_setup')

    def is_mod(self, elder: str = None):
        if elder == None:
            return self.role >= 1
        if elder != 'elder':
            raise error.InvalidArgument()
        else:
            return self.role == 2
    
    def has_cp(self):
        return self.cp > 0
    
    def attached(self):
        return self.options.get('attached')
    
    #MAKE UNION OF TWO FUNCTIONS BELOW
    #ALSO, GET A L L COMMENTS AVAILABLE
    def get_comment_history(self, paginate = False, per_page = 10):
        from .classconverter import class_converter
        route = Route.GET_COMMENT_HISTORY
        params = Params().create_new().put_definer('userid', str(self.id)).put_page(0).put_total(0).put_mode(0).finish()
        resp = http.SendHTTPRequest(route, params)
        to_map = resp.split('#')
        comments = []; D = {'name': self.name, 'id': self.id, 'account_id': self.account_id}
        if (len(to_map[0])==0):
            raise error.NothingFound('comments')
        else:
            to_map = mapper_util.normalize(to_map[0]).split('|')
            for element in to_map:
                temp = element.split(':')[0].split('~')
                to_put = ['TYPE', '0']; temp.extend(to_put)
                mapped = mapper_util.map(temp)
                comments.append(class_converter.CommentConvert(mapped, self, D))
            if not paginate:
                return comments
            else:
                paginated = pagin(comments, per_page=per_page)
                return paginated

    def get_comments(self, paginate = False, per_page = 10):
        from .classconverter import class_converter
        route = Route.GET_COMMENTS
        parameters = Params().create_new().put_definer('accountid', str(self.account_id)).put_page(0).put_total(0).finish()
        resp = http.SendHTTPRequest(route, parameters)
        to_map = resp.split('#')
        comments = []; D = {'name': self.name, 'id': self.id, 'account_id': self.account_id}
        if (len(to_map[0])==0):
            raise error.NothingFound('comments')
        else:
            to_map = mapper_util.normalize(to_map[0]).split('|') #I don't know why but this one is actually intended
            for element in to_map:
                temp = element.split('~')
                to_put = ['TYPE', '1']; temp.extend(to_put)
                mapped = mapper_util.map(temp)
                comments.append(class_converter.CommentConvert(mapped, self, D))
            if not paginate:
                return comments
            else:
                paginated = pagin(comments, per_page=per_page)
                return paginated

    def update(self):
        from .client import client
        self.options = client().get_user(self.account_id, attached=self.attached()).options
        return None

# client = gd.client()
# user = client.get_user(71) //returns gd.User() object, for instance, RobTop
# print(user.is_mod('elder'), user.has_cp(), user.cp) //returns (True, False, 0)