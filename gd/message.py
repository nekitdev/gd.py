from .abstractentity import AbstractEntity
from .abstractuser import AbstractUser
from .session import _session

from .utils.enums import MessageOrRequestType
from .utils.wrap_tools import make_repr, check

class Message(AbstractEntity):
    """Class that represents private messages in Geometry Dash.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
        self._body = options.pop('body', '')

    def __repr__(self):
        info = {
            'author': self.author,
            'id': self.id,
            'is_read': self.is_read()
        }
        return make_repr(self, info)

    @property
    def author(self):
        """:class:`.AbstractUser`: An author of the message."""
        return self.options.get('author', AbstractUser())

    @property
    def recipient(self):
        """:class:`.AbstractUser`: A recipient of the message."""
        return self.options.get('recipient', AbstractUser())

    @property
    def subject(self):
        """:class:`str`: A subject of the message, as string."""
        return self.options.get('subject', '')

    @property
    def timestamp(self):
        """:class:`str`: A human-readable string representing how long ago message was created."""
        return self.options.get('timestamp', 'unknown')

    @property
    def type(self):
        """:class:`.MessageOrRequestType`: Whether a message is sent or inbox."""
        return self.options.get('type', MessageOrRequestType(0))

    @property
    def body(self):
        """Union[:class:`str`, ``None``]: A body of the message. Requires :meth:`.Message.read`."""
        return self._body

    def is_read(self):
        """:class:`bool`: Indicates whether message is read or not."""
        return self.options.get('is_read', False)

    @check.is_logged()
    async def read(self):
        """|coro|

        Read a message. Set the body of the message to the content.

        Returns
        -------
        :class:`str`
            The content of the message.
        """
        return await _session.read_message(self)

    @check.is_logged()
    async def delete(self):
        """|coro|

        Delete a message.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a message.
        """
        await _session.delete_message(self)
