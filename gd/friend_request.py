from gd.abstractentity import AbstractEntity
from gd.abstractuser import AbstractUser

from gd.typing import Client, FriendRequest, Union

from gd.utils.enums import MessageOrRequestType
from gd.utils.indexer import Index
from gd.utils.parser import ExtDict
from gd.utils.text_tools import make_repr
from gd.utils.crypto.coders import Coder


class FriendRequest(AbstractEntity):
    """Class that represents a friend request.
    This class is derived from :class:`.AbstractEntity`.
    """

    def __repr__(self) -> str:
        info = {"id": self.id, "author": self.author, "type": self.type}
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.body)

    @classmethod
    def from_data(
        cls, data: ExtDict, user_2: Union[ExtDict, AbstractUser], client: Client
    ) -> FriendRequest:
        user_1 = AbstractUser(
            name=data.get(Index.REQUEST_SENDER_NAME, "unknown"),
            id=data.getcast(Index.REQUEST_SENDER_ID, 0, int),
            account_id=data.getcast(Index.REQUEST_SENDER_ACCOUNT_ID, 0, int),
            client=client,
        )
        if isinstance(user_2, ExtDict):
            user_2 = AbstractUser(**user_2, client=client)

        indicator = data.getcast(Index.REQUEST_INDICATOR, 0, int)
        is_normal = indicator ^ 1

        return cls(
            id=data.getcast(Index.REQUEST_ID, 0, int),
            timestamp=str(data.get(Index.REQUEST_TIMESTAMP, "unknown")),
            body=Coder.do_base64(data.get(Index.REQUEST_BODY, ""), encode=False, errors="replace"),
            is_read=(not data.get(Index.REQUEST_STATUS)),
            author=(user_1 if is_normal else user_2),
            recipient=(user_2 if is_normal else user_1),
            type=MessageOrRequestType.from_value(indicator, 0),
            client=client,
        )

    @property
    def author(self) -> AbstractUser:
        """:class:`.AbstractUser`: An author of the friend request."""
        return self.options.get("author", AbstractUser(client=self.client))

    @property
    def recipient(self) -> AbstractUser:
        """:class:`.AbstractUser`: A recipient of the friend request."""
        return self.options.get("recipient", AbstractUser(client=self.client))

    @property
    def type(self) -> MessageOrRequestType:
        """:class:`.MessageOrRequestType`: Whether request is incoming or sent."""
        return MessageOrRequestType.from_value(self.options.get("type", 0))

    @property
    def body(self) -> str:
        """:class:`str`: A string representing a message request was sent with."""
        return self.options.get("body", "")

    @property
    def timestamp(self) -> str:
        """:class:`str`: A human-readable string representing how long ago request was created."""
        return self.options.get("timestamp", "unknown")

    def is_read(self) -> bool:
        """:class:`bool`: Indicates whether request was already read."""
        return self.options.get("is_read", False)

    async def read(self) -> None:
        """|coro|

        Read a friend request. Sets ``is_read`` to ``True`` on success.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to read a request.
        """
        await self.client.read_friend_request(self)

    async def delete(self) -> None:
        """|coro|

        Delete a friend request.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a request.
        """
        await self.client.delete_friend_request(self)

    async def accept(self) -> None:
        """|coro|

        Accept a friend request.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to accept a request.
        """
        await self.client.accept_friend_request(self)
