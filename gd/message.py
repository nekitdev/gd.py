from .abstractentity import AbstractEntity
from .session import GDSession

from .utils.wrap_tools import _make_repr, check
from .utils.context import ctx

_session = GDSession()

class Message(AbstractEntity):
    """Class that represents private messages in Geometry Dash."""
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
        """:class:`.AbstractUser`: An author of the message."""
        return self.options.get('author')

    @property
    def recipient(self):
        """:class:`.AbstractUser`: A recipient of the message."""
        return self.options.get('recipient')

    @property
    def subject(self):
        """:class:`str`: A subject of the message, as string."""
        return self.options.get('subject')

    @property
    def timestamp(self):
        """:class:`str`: A human-readable string representing how long ago message was created."""
        return self.options.get('timestamp')

    @property
    def typeof(self):
        """:class:`str`: Whether a message is sent or inbox. ('sent' or 'normal')"""
        return self.options.get('type')

    @property
    def body(self):
        """Union[:class:`str`, ``None``]: A body of the message. Requires :meth:`.Message.read`."""
        return self._body

    def is_read(self):
        """:class:`bool`: Indicates whether message is read or not."""
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
        return await _session.read_message(self)

    @check.is_logged(ctx)
    async def delete(self):
        """|coro|

        Delete a message.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a message.
        """
        await _session.delete_message(self)

