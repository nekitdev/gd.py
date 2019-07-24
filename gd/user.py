# from .errors import error
from .utils.http_request import http
from .utils.routes import Route
from .utils.params import Parameters as Params
from .utils.mapper import mapper_util
from .utils.gdpaginator import paginate as pagin
from .abstractentity import AbstractEntity
import urllib
#TO_DO: add __str__ and __repr__ funcs
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

    def get_comment_history(self, pages = 1, paginate = False, per_page = 10):
        final = []
        for i in range(pages):
            try:
                temp = retrieve_comments(
                    obj = self, route = Route.GET_COMMENT_HISTORY, type_num = 0, paginate = paginate, per_page = per_page,
                    params = Params().create_new().put_definer('userid', str(self.id)).put_page(i).put_total(0).put_mode(0).finish()
                )
                final.extend(temp)
            except (urllib.error.URLError, error.NothingFound):
                break
        return final    

    def get_comments(self, pages = 1, paginate = False, per_page = 10):
        final = []
        for i in range(pages):
            try:
                temp = retrieve_comments(
                    obj = self, route = Route.GET_COMMENTS, type_num = 1, paginate = paginate, per_page = per_page,
                    params = Params().create_new().put_definer('accountid', str(self.account_id)).put_page(i).put_total(0).finish()
                )
                final.extend(temp)
            except (urllib.error.URLError, error.NothingFound):
                break
        return final

    def update(self):
        from .client import client
        self.options = client().get_user(self.account_id, attached=self.attached()).options
        return None

def retrieve_comments(obj, route: str, params: dict, type_num: int, paginate: bool, per_page: int):
    from .classconverter import class_converter
    resp = http.send_request(route, params)
    to_map = resp.split('#')
    comments = []; D = {'name': obj.name, 'id': obj.id, 'account_id': obj.account_id}
    if (len(to_map[0]) == 0):
        raise error.NothingFound('comments')
    else:
        to_map = mapper_util.normalize(to_map[0]).split('|')
        for element in to_map:
            temp = (element.split(':')[0].split('~')) if (type_num == 0) else (element.split('~'))
            to_put = ['TYPE', str(type_num)]; temp.extend(to_put)
            mapped = mapper_util.map(temp)
            comments.append(class_converter.CommentConvert(mapped, obj, D))
        if not paginate:
            return comments
        else:
            paginated = pagin(comments, per_page=per_page)
            return paginated

# client = gd.client()
# user = client.get_user(71) //returns gd.User() object, for instance, RobTop
# print(user.is_mod('elder'), user.has_cp(), user.cp) //returns (True, False, 0)