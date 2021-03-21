from gd.abstract_entity import AbstractEntity
from gd.datetime import datetime
from gd.enums import FriendRequestType
from gd.model import FriendRequestModel  # type: ignore
from gd.text_utils import make_repr
from gd.typing import TYPE_CHECKING, Optional
from gd.user import User

__all__ = ("FriendRequest",)


if TYPE_CHECKING:
    from gd.client import Client  # noqa


class FriendRequest(AbstractEntity):
    """Class that represents a friend request.
    This class is derived from :class:`~gd.AbstractEntity`.

    .. container:: operations

        .. describe:: x == y

            Check if two objects are equal. Compared by hash and type.

        .. describe:: x != y

            Check if two objects are not equal.

        .. describe:: str(x)

            Return content of the friend request.

        .. describe:: repr(x)

            Return representation of the friend request, useful for debugging.

        .. describe:: hash(x)

            Returns ``hash(self.hash_str)``.
    """

    def __repr__(self) -> str:
        info = {"id": self.id, "author": self.author, "type": self.type}
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.content)

    @classmethod
    def from_model(  # type: ignore
        cls,
        model: FriendRequestModel,
        *,
        client: Optional["Client"] = None,
        other_user: Optional[User] = None,
        type: FriendRequestType = FriendRequestType.INCOMING,  # type: ignore
    ) -> "FriendRequest":
        return cls(
            inner_user=User(
                name=model.name,
                id=model.user_id,
                icon_id=model.icon_id,
                color_1_id=model.color_1_id,
                color_2_id=model.color_2_id,
                icon_type=model.icon_type,
                has_glow=model.has_glow,
                account_id=model.account_id,
                client=client,
            ),
            id=model.id,
            content=model.content,
            created_at=model.created_at,
            unread=model.unread,
            read=model.read,
            other_user=(other_user if other_user else User()).attach_client(client),
            type=type,
            client=client,
        )

    @property
    def author(self) -> User:
        """:class:`~gd.User`: Author of the friend request."""
        return self.inner_user if self.is_incoming() else self.other_user

    @property
    def recipient(self) -> User:
        """:class:`~gd.User`: Recipient of the friend request."""
        return self.other_user if self.is_incoming() else self.inner_user

    @property
    def inner_user(self) -> User:
        return self.options.get("inner_user", User(client=self.client_unchecked))

    @property
    def other_user(self) -> User:
        return self.options.get("other_user", User(client=self.client_unchecked))

    @property
    def type(self) -> FriendRequestType:
        """:class:`~gd.FriendRequestType`: Whether request is incoming or sent."""
        return FriendRequestType.from_value(self.options.get("type", FriendRequestType.INCOMING))

    @property
    def content(self) -> str:
        """:class:`str`: Friend request message."""
        return self.options.get("content", "")

    def is_incoming(self) -> bool:
        return self.type is FriendRequestType.INCOMING

    def is_outgoing(self) -> bool:
        return self.type is FriendRequestType.OUTGOING

    body = content

    @property
    def created_at(self) -> Optional[datetime]:
        """Optional[:class:`~datetime.datetime`]:
        Timestamp representing when friend request was created.
        """
        return self.options.get("created_at")

    def is_read(self) -> bool:
        """:class:`bool`: Indicates whether request was read."""
        return bool(self.options.get("read"))

    async def read(self) -> None:
        """Read a friend request. Sets ``is_read`` to ``True`` on success.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to read a request.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.read_friend_request(self)

    async def delete(self) -> None:
        """Delete a friend request.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to delete a request.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.delete_friend_request(self)

    async def accept(self) -> None:
        """Accept a friend request.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to accept a request.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.accept_friend_request(self)
