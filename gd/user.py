from .utils.http_request import http
from .utils.routes import Route
from .utils.params import Parameters as Params
from .utils.mapper import mapper_util
from .utils.gdpaginator import paginate as pagin
from .abstractentity import AbstractEntity
from .errors import MissingAccess, NothingFound
from .comment import Comment
from .utils.context import ctx
from .utils.wrap_tools import _make_repr, check

#TO_DO: add __repr__ func

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

    @property
    def _dict_for_parse(self):
        return {
            k: getattr(self, k) for k in ('name', 'id', 'account_id')
        }
    

    def is_mod(self, elder: str = None):
        if elder == None:
            return self.role >= 1
        if elder == 'elder':
            return self.role == 2
        raise TypeError("is_mod(elder) expected elder=='elder', or None.")
    
    def has_cp(self):
        return self.cp > 0

    async def get_comments(self, page: int = 0):
        """|coro|

        Gets comments on a specific page. Returns ``None`` if nothing was found.

        Parameters
        ----------
        page: :class:`int`
            Page to look comments at.

        Returns
        -------
        List[:class:`.Comment`]
            List of all comments retrieved, if found.

        Raises
        :exc:`.NothingFound`
            No comments were found.
        """
        params = Params().create_new().put_definer('accountid', str(self.account_id)).put_page(page).put_total(0).finish()
        resp = await http.fetch(Route.GET_COMMENTS, params, splitter='#')
        thing = resp[0]
        if len(thing) == 0:
            raise NothingFound(Comment)
        to_map = mapper_util.normalize(thing).split('|')
        return [
            class_converter.CommentConvert(
                mapper_util.map(elem.split('~') + ['101', '1']), self._dict_for_parse
            ) for elem in to_map
        ]


# Comment history: Params().create_new().put_definer('userid', str(self.id)).put_page(i).put_total(0).put_mode(0).finish()

    @check.is_logged(ctx)
    async def send(self, subject: str, body: str):
        """|coro|

        Send the message to ``self``. Requires logged client.

        Parameters
        ----------
        subject: :class:`str`
            The subject of the message.

        body: :class:`str`
            The body of the message.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to send a message.
        """
        params = Params().create_new().put_definer('accountid', str(ctx.account_id)).put_message(subject, body).put_recipient(str(self.account_id)).put_password(ctx.encodedpass).finish()
        resp = await http.request(Route.SEND_PRIVATE_MESSAGE, params)
        if resp != 1:
            raise MissingAccess(f"Failed to send a message to a user: {self!r}.")
        
    async def update(self):
        """|coro|

        Update the user's statistics and other parameters.
        """
        from .client import Client
        self.options = Client().get_user(self.account_id).options

# client = gd.client()
# user = client.get_user(71) //returns gd.User() object, for instance, RobTop
# print(user.is_mod('elder'), user.has_cp(), user.cp) //returns (True, False, 0)