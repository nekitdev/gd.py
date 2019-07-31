import base64

from .abstractentity import AbstractEntity
from .errors import MissingAccess
from .utils.http_request import http
from .utils.routes import Route
from .utils.indexer import Index as i
from .utils.crypto.coders import Coder
from .utils.mapper import mapper_util
from .utils.params import Parameters as Params
from .utils.wrap_tools import _make_repr, check
from .utils.context import ctx

class Message(AbstractEntity):
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
        self._body = None
    
    def __repr__(self):
        info = {
            'author': self.author,
            'body': repr(self.body),
            'id': self.id,
            'is_read': self.is_read()
        }
        return _make_repr(self, info)

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

    def is_read(self):
        return self.options.get('is_read')

    @check.is_logged(ctx)
    async def read(self):
        """|coro|

        Read a message. Set the body of the message to the content.

        Returns
        -------
        :class:`str`
            The content of the message.
        """
        params = Params().create_new().put_definer('accountid', str(ctx.account_id)).put_definer('messageid', str(self.id)).put_password(ctx.encodedpass).put_is_sender(self.typeof).finish()
        resp = await http.fetch(Route.READ_PRIVATE_MESSAGE, params, splitter=':', should_map=True)
        ret = Coder().decode0(
            type='message', string=mapper_util.normalize(resp.get(i.MESSAGE_BODY))
        )
        self._body = ret
        return self.body

    @check.is_logged(ctx)
    async def delete(self):
        """|coro|

        Delete a message.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a message.
        """
        params = Params().create_new().put_definer('accountid', str(ctx.account_id)).put_definer('messageid', str(self.id)).put_password(ctx.encodedpass).put_is_sender(self.typeof).finish()
        resp = await http.fetch(Route.DELETE_PRIVATE_MESSAGE, params)
        if resp != 1:
            raise MissingAccess(message=f"Failed to delete a message: {self!r}.")
