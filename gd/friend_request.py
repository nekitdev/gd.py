from .abstractentity import AbstractEntity
from .errors import MissingAccess
from .utils.params import Parameters as Params
from .utils.routes import Route
from .utils.http_request import http
from .utils.context import ctx
from .utils.wrap_tools import _make_repr, check

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

    @check.is_logged(ctx)
    async def delete(self):
        """|coro|

        Delete a friend request.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a request.
        """
        user = self.author if self.typeof == 'normal' else self.recipient
        params = Params().create_new().put_definer('accountid', str(ctx.account_id)).put_definer('user', str(user.account_id)).put_password(c.encodedpass).put_is_sender(self.typeof).finish()
        resp = await http.request(Route.DELETE_REQUEST, params)
        if resp != 1:
            raise MissingAccess(message=f'Failed to delete a friend request: {self!r}.')

    @check.is_logged(ctx)
    async def accept(self):
        """|coro|

        Accept a friend request.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to accept a request.
        """
        if self.typeof == 'sent':
            raise MissingAccess(
                "Failed to accept a friend request. Reason: request is sent, not recieved one."
            )
        params = Params().create_new().put_definer('accountid', str(ctx.account_id)).put_password(ctx.encodedpass).put_definer('user', str(self.author.account_id)).put_definer('requestid', str(self.id)).finish()
        resp = await http.request(Route.ACCEPT_REQUEST, params)
        if resp != 1:
            raise MissingAccess(message=f"Failed to accept a friend request: {self!r}.")
