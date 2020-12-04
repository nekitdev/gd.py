from gd.abstract_entity import AbstractEntity
from gd.datetime import datetime
from gd.enums import MessageType
from gd.model import MessageModel  # type: ignore
from gd.text_utils import make_repr
from gd.typing import TYPE_CHECKING, Optional
from gd.user import User

if TYPE_CHECKING:
    from gd.client import Client  # noqa

__all__ = ("Message",)


class Message(AbstractEntity):
    """Class that represents private messages in Geometry Dash.
    This class is derived from :class:`~gd.AbstractEntity`.

    .. container:: operations

        .. describe:: x == y

            Check if two objects are equal. Compared by hash and type.

        .. describe:: x != y

            Check if two objects are not equal.

        .. describe:: str(x)

            Return content of the message. Empty if the message was not read yet.

        .. describe:: repr(x)

            Return representation of the message, useful for debugging.

        .. describe:: hash(x)

            Returns ``hash(self.hash_str)``.
    """

    SCHEMA = "Re: {message.subject}"

    def __repr__(self) -> str:
        info = {"author": self.author, "id": self.id, "is_read": self.is_read()}
        return make_repr(self, info)

    def __str__(self) -> str:
        if self.content is None:
            return ""

        return str(self.content)

    @classmethod
    def from_model(  # type: ignore
        cls,
        model: MessageModel,
        *,
        client: Optional["Client"] = None,
        other_user: Optional[User] = None,
        type: MessageType = MessageType.NORMAL,  # type: ignore
    ) -> "Message":
        return cls(
            inner_user=User(
                name=model.name, id=model.user_id, account_id=model.account_id, client=client,
            ),
            id=model.id,
            subject=model.subject,
            content=model.content,
            created_at=model.created_at,
            read=model.read,
            unread=model.unread,
            other_user=(other_user if other_user else User()).attach_client(client),
            client=client,
        )

    @property
    def author(self) -> User:
        """:class:`~gd.User`: Author of the message."""
        return self.inner_user if self.is_normal() else self.other_user

    @property
    def recipient(self) -> User:
        """:class:`~gd.User`: Recipient of the message."""
        return self.other_user if self.is_normal() else self.inner_user

    @property
    def inner_user(self) -> User:
        return self.options.get("inner_user", User(client=self.client_unchecked))

    @property
    def other_user(self) -> User:
        return self.options.get("other_user", User(client=self.client_unchecked))

    @property
    def subject(self) -> str:
        """:class:`str`: A subject of the message, as string."""
        return self.options.get("subject", "")

    @property
    def created_at(self) -> Optional[datetime]:
        """Optional[:class:`~datetime.datetime`]:
        Timestamp representing when the message was created.
        """
        return self.options.get("created_at")

    @property
    def type(self) -> MessageType:
        """:class:`~gd.MessageType`: Whether a message is sent or incoming."""
        return MessageType.from_value(self.options.get("type", MessageType.NORMAL))

    def is_normal(self) -> bool:
        return self.type is MessageType.NORMAL

    def get_content(self) -> Optional[str]:
        """Optional[:class:`str`]: Content of the message. Requires :meth:`~gd.Message.read`."""
        return self.options.get("content")

    def set_content(self, content: str) -> None:
        """Set ``self.content`` to ``content``."""
        self.options.update(content=content)

    content = property(get_content, set_content)
    body = content

    def is_read(self) -> bool:
        """:class:`bool`: Indicates whether message is read or not."""
        return bool(self.options.get("read"))

    async def update(self) -> None:
        message = await self.client.get_message(self.id, self.type)
        self.options.update(message.options)

    async def read(self) -> str:
        """Read a message. Set the body of the message to the content.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to read a message.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.

        Returns
        -------
        :class:`str`
            The content of the message.
        """
        if self.content is None:
            await self.update()

        return str(self.content)

    async def reply(self, content: str, schema: Optional[str] = None) -> Optional["Message"]:
        """Reply to the message. Format the subject according to schema.

        Schema format can only contain ``{message.attribute}`` elements.

        Content also allows schema format.

        Example:

        .. code-block:: python3

            await message.reply(
                content="Replying to message by {message.author.name}."
                schema="Re: {message.subject} ({message.rating})"
            )

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to read a message.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.

        Returns
        -------
        Optional[:class:`~gd.Message`]
            Sent message, or ``None`` if :attr:`~gd.Client.load_after_post` is ``False``.
        """
        if schema is None:
            schema = self.SCHEMA

        content, subject = content.format(message=self), schema.format(message=self)

        return await self.author.send(subject, content)

    async def delete(self) -> None:
        """Delete a message.

        Raises
        ------
        :exc:`gd.MissingAccess`
            Failed to delete a message.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.delete_message(self)
