from .abstractentity import AbstractEntity
from .session import GDSession

from .utils.context import ctx
from .utils.wrap_tools import _make_repr, check

_session = GDSession()

class FriendRequest(AbstractEntity):
    """Class that represents a friend request."""
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
        
    @property
    def author(self):
        """:class:`.AbstractUser`: An author of the friend request."""
        return self.options.get('author')

    @property
    def recipient(self):
        """:class:`.AbstractUser`: A recipient of the friend request."""
        return self.options.get('recipient')

    @property
    def typeof(self):
        """:class:`str`: Whether request is incoming or sent. ('sent' or 'normal')"""
        return self.options.get('type')

    @property
    def body(self):
        """:class:`str`: A string representing a message request was sent with."""
        return self.options.get('body')

    @property
    def timestamp(self):
        """:class:`str`: A human-readable string representing how long ago request was created."""
        return self.options.get('timestamp')

    def is_read(self):
        """:class:`bool`: Indicates whether request was already read."""
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
        await _session.delete_friend_req(self)

    @check.is_logged(ctx)
    async def accept(self):
        """|coro|

        Accept a friend request.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to accept a request.
        """
        await _session.accept_friend_req(self)
