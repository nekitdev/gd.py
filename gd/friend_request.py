from .abstractentity import AbstractEntity
from .abstractuser import AbstractUser

from .utils.decorators import check_logged
from .utils.enums import MessageOrRequestType
from .utils.text_tools import make_repr


class FriendRequest(AbstractEntity):
    """Class that represents a friend request.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __repr__(self) -> str:
        info = {
            'id': self.id,
            'author': self.author,
            'type': self.type
        }
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.body)

    @property
    def author(self) -> AbstractUser:
        """:class:`.AbstractUser`: An author of the friend request."""
        return self.options.get('author', AbstractUser())

    @property
    def recipient(self) -> AbstractUser:
        """:class:`.AbstractUser`: A recipient of the friend request."""
        return self.options.get('recipient', AbstractUser())

    @property
    def type(self) -> MessageOrRequestType:
        """:class:`.MessageOrRequestType`: Whether request is incoming or sent."""
        return MessageOrRequestType.from_value(self.options.get('type', 0))

    @property
    def body(self) -> str:
        """:class:`str`: A string representing a message request was sent with."""
        return self.options.get('body', '')

    @property
    def timestamp(self) -> str:
        """:class:`str`: A human-readable string representing how long ago request was created."""
        return self.options.get('timestamp', 'unknown')

    def is_read(self) -> bool:
        """:class:`bool`: Indicates whether request was already read."""
        return self.options.get('is_read', False)

    @check_logged
    async def read(self) -> None:
        """|coro|

        Read a friend request. Sets ``is_read`` to ``True`` on success.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to read a message.
        """
        await self.client.read_friend_request(self)

    @check_logged
    async def delete(self) -> None:
        """|coro|

        Delete a friend request.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a request.
        """
        await self.client.delete_friend_request(self)

    @check_logged
    async def accept(self) -> None:
        """|coro|

        Accept a friend request.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to accept a request.
        """
        await self.client.accept_friend_request(self)
