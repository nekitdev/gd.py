from .typing import Optional

from .abstractentity import AbstractEntity
from .abstractuser import AbstractUser

from .utils.decorators import check_logged
from .utils.enums import MessageOrRequestType
from .utils.text_tools import make_repr


class Message(AbstractEntity):
    """Class that represents private messages in Geometry Dash.
    This class is derived from :class:`.AbstractEntity`.
    """
    SCHEMA = 'Re: {msg.subject}'

    def __init__(self, **options) -> None:
        super().__init__(**options)
        self._body = options.pop('body', '')

    def __repr__(self) -> str:
        info = {
            'author': self.author,
            'id': self.id,
            'is_read': self.is_read()
        }
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.subject)

    @property
    def author(self) -> AbstractUser:
        """:class:`.AbstractUser`: An author of the message."""
        return self.options.get('author', AbstractUser())

    @property
    def recipient(self) -> AbstractUser:
        """:class:`.AbstractUser`: A recipient of the message."""
        return self.options.get('recipient', AbstractUser())

    @property
    def subject(self) -> str:
        """:class:`str`: A subject of the message, as string."""
        return self.options.get('subject', '')

    @property
    def timestamp(self) -> str:
        """:class:`str`: A human-readable string representing how long ago message was created."""
        return self.options.get('timestamp', 'unknown')

    @property
    def type(self) -> MessageOrRequestType:
        """:class:`.MessageOrRequestType`: Whether a message is sent or inbox."""
        return MessageOrRequestType.from_value(self.options.get('type', 0))

    @property
    def body(self) -> Optional[str]:
        """Optional[:class:`str`]: A body of the message. Requires :meth:`.Message.read`."""
        return self._body

    def is_read(self) -> bool:
        """:class:`bool`: Indicates whether message is read or not."""
        return bool(self.options.get('is_read'))

    @check_logged
    async def read(self) -> str:
        """|coro|

        Read a message. Set the body of the message to the content.

        Returns
        -------
        :class:`str`
            The content of the message.
        """
        return await self.client.read_message(self)

    @check_logged
    async def reply(self, content: str, schema: Optional[str] = None) -> None:
        """|coro|

        Reply to the message. Format the subject according to schema.

        Schema format can only contain ``{msg.attr}`` elements.

        Content also allows schema format.

        Example:

        .. code-block:: python3

            await message.reply(
                content='Replying to message by {msg.author.name}.'
                schema='Re: {msg.subject} ({msg.rating})'
            )
        """
        if schema is None:
            schema = self.SCHEMA

        content, subject = content.format(msg=self), schema.format(msg=self)

        await self.author.send(subject, content)

    @check_logged
    async def delete(self) -> None:
        """|coro|

        Delete a message.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a message.
        """
        await self.client.delete_message(self)
