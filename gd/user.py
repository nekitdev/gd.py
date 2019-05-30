from .utils.errors import error
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
    def status(self):
        return self.options.get('status')
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
    def pm_policy(self):
        return self.options.get('messages')
    @property
    def friend_req_policy(self):
        return self.options.get('friend_requests')
    @property
    def comments_policy(self):
        return self.options.get('comments')

    def is_mod(self, elder: str = None):
        if elder == None:
            return self.role >= 1
        if elder != 'elder':
            raise error.InvalidArgument()
        else:
            return self.role == 2
    
    def has_cp(self):
        return self.cp > 0

    def get_icon_setup(self):
        return self.options.get('icon_setup')

# client = gd.client()
# user = client.get_user(71) //returns gd.User() object, for instance, RobTop
# print(user.is_mod('elder'), user.has_cp(), user.cp) //returns (True, False, 0)
