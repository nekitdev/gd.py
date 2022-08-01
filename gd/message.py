from __future__ import annotations

from typing import ClassVar, Optional, TypeVar

from gd.constants import EMPTY
from gd.entity import Entity
from gd.enums import MessageType

# from gd.models import MessageModel
from gd.user import User

__all__ = ("Message",)

M = TypeVar("M", bound="Message")


class Message(Entity):
    SCHEMA: ClassVar[str] = "Re: {message.subject}"

    user: User
    type: MessageType

    subject: str = EMPTY
    content: Optional[str] = None

    was_read: bool = False

    def __str__(self) -> str:
        content = self.content

        return EMPTY if content is None else content

    def is_incoming(self) -> bool:
        return self.type.is_incoming()

    def is_outgoing(self) -> bool:
        return self.type.is_outgoing()

    @property
    def body(self) -> Optional[str]:
        return self.content

    def is_read(self) -> bool:
        return self.was_read

    def is_unread(self) -> bool:
        return not self.was_read

    async def read(self) -> str:
        content = self.content

        if content is None:
            message = await self.client.get_message(self.id, self.type)

            self.content = content = message.content

        return content

    async def reply(self, content: str, schema: Optional[str] = None) -> Optional[Message]:
        if schema is None:
            schema = self.SCHEMA

        content = content.format(message=self)
        subject = schema.format(message=self)

        return await self.user.send(subject, content)

    async def delete(self) -> None:
        await self.client.delete_message(self)
