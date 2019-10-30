from .abstractentity import AbstractEntity
from .abstractuser import AbstractUser

from .session import _session

from .utils.enums import MessageOrRequestType
from .utils.wrap_tools import make_repr, check

class FriendRequest(AbstractEntity):
    """Class that represents a friend request.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options

    def __repr__(self):
        info = {
            'id': self.id,
            'author': self.author,
            'type': self.type
        }
        return make_repr(self, info)

    @property
    def author(self):
        """:class:`.AbstractUser`: An author of the friend request."""
        return self.options.get('author', AbstractUser())

    @property
    def recipient(self):
        """:class:`.AbstractUser`: A recipient of the friend request."""
        return self.options.get('recipient', AbstractUser())

    @property
    def type(self):
        """:class:`.MessageOrRequestType`: Whether request is incoming or sent."""
        return self.options.get('type', MessageOrRequestType(0))

    @property
    def body(self):
        """:class:`str`: A string representing a message request was sent with."""
        return self.options.get('body', '')

    @property
    def timestamp(self):
        """:class:`str`: A human-readable string representing how long ago request was created."""
        return self.options.get('timestamp', 'unknown')

    def is_read(self):
        """:class:`bool`: Indicates whether request was already read."""
        return self.options.get('is_read', False)

    @check.is_logged()
    async def read(self):
        """|coro|

        Read a friend request. Sets ``is_read`` to ``True`` on success.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to read a message.
        """
        await _session.read_friend_req(self)

    @check.is_logged()
    async def delete(self):
        """|coro|

        Delete a friend request.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a request.
        """
        await _session.delete_friend_req(self)

    @check.is_logged()
    async def accept(self):
        """|coro|

        Accept a friend request.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to accept a request.
        """
        await _session.accept_friend_req(self)
