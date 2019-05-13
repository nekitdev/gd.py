from .utils.errors import error

class User:
    def __init__(self, **options):
        self._name = options.get('name')
        self._account_id = options.get('account_id')
        self._id = options.get('_id')
        self._stars = options.get('stars')
        self._demons = options.get('demons')
        self._cp = options.get('cp')
        self._diamonds = options.get('diamonds')
        self._role = options.get('role')
        self._status = options.get('status')
        self._global_rank = options.get('global_rank')
        self._youtube = options.get('youtube')
        self._twitter_stuff = options.get('twitter')
        self._twitch_stuff = options.get('twitch')
        self._messages = options.get('messages')
        self._friend_requests = options.get('friend_requests')
        self._comments = options.get('comments')
        self._icon_setup = options.get('icon_setup')

    @property
    def name(self):
        return self._name
    @property
    def account_id(self): #for nerds and for me
        return self._account_id
    @property
    def id(self):
        return self._id
    @property
    def stars(self):
        return self._stars
    @property
    def demons(self):
        return self._demons
    @property
    def cp(self):
        return self._cp
    @property
    def diamonds(self):
        return self._diamonds
    @property
    def role(self):
        return self._role
    @property
    def status(self):
        return self._status
    @property
    def rank(self):
        return self._global_rank
    @property
    def youtube(self):
        return self._youtube
    @property
    def twitter(self):
        return self._twitter_stuff[0]
    @property
    def twitter_link(self):
        return self._twitter_stuff[1]
    @property
    def twitch(self):
        return self._twitch_stuff[0]
    @property
    def twitch_link(self):
        return self._twitch_stuff[1]
    @property
    def pm_policy(self):
        return self._messages
    @property
    def friend_req_policy(self):
        return self._friend_requests
    @property
    def comments_policy(self):
        return self._comments

    def is_mod(self, elder: str = None):
        if elder == None:
            return self.role == 1
        if elder != 'elder':
            raise error.InvalidArgument()
        else:
            return self.role == 2
    
    def has_cp(self):
        return self.cp > 0

    def get_icon_setup(self):
        return self._icon_setup

# client = gd.client()
# user = client.get_user(71) //returns gd.User() object, for instance, RobTop
# print(user.is_mod('elder'), user.has_cp(), user.cp) //returns (True, False, 0)
