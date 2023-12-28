from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Optional

from attrs import define, field
from pendulum import DateTime

from gd.constants import DEFAULT_READ
from gd.date_time import utc_now
from gd.entity import Entity
from gd.enums import MessageType
from gd.errors import ClientError
from gd.users import UserReference

if TYPE_CHECKING:
    from typing_extensions import Self

    from gd.client import Client
    from gd.models import MessageModel

__all__ = ("Message",)

NO_SUBJECT = "(no subject)"

NO_CONTENT = "no content; use `await message.read()` to read the message"

READ_FAILED = "read failed (no content)"


@define()
class MessageReference(Entity):
    user: UserReference = field(eq=False)
    type: MessageType = field(eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def is_incoming(self) -> bool:
        return self.type.is_incoming()

    def is_outgoing(self) -> bool:
        return self.type.is_outgoing()

    async def delete(self) -> None:
        await self.client.delete_message(self)

    def attach_client_unchecked(self, client: Optional[Client]) -> Self:
        self.user.attach_client_unchecked(client)

        return super().attach_client_unchecked(client)

    def attach_client(self, client: Client) -> Self:
        self.user.attach_client(client)

        return super().attach_client(client)

    def detach_client(self) -> Self:
        self.user.detach_client()

        return super().detach_client()


@define()
class Message(MessageReference):
    SCHEMA: ClassVar[str] = "Re: {message.subject}"

    created_at: DateTime = field(factory=utc_now, eq=False)

    subject_unchecked: Optional[str] = field(default=None, eq=False)
    content_unchecked: Optional[str] = field(default=None, eq=False)

    was_read: bool = field(default=DEFAULT_READ, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @property
    def subject(self) -> str:
        return self.subject_unchecked or NO_SUBJECT

    @subject.setter
    def subject(self, subject: str) -> None:
        self.subject_unchecked = subject

    @subject.deleter
    def subject(self) -> None:
        self.subject_unchecked = None

    @property
    def content(self) -> str:
        content = self.content_unchecked

        if content is None:
            raise ClientError(NO_CONTENT)

        return content

    @content.setter
    def content(self, content: str) -> None:
        self.content_unchecked = content

    @content.deleter
    def content(self) -> None:
        self.content_unchecked = None

    def has_content(self) -> bool:
        return self.content_unchecked is not None

    def __str__(self) -> str:
        return self.subject

    @classmethod
    def from_model(cls, model: MessageModel) -> Self:
        type = MessageType.OUTGOING if model.is_sent() else MessageType.INCOMING

        return cls(
            id=model.id,
            user=UserReference(id=model.user_id, name=model.name, account_id=model.account_id),
            type=type,
            created_at=model.created_at,
            subject_unchecked=model.subject or None,
            content_unchecked=model.content if model.has_content() else None,
            was_read=model.read,
        )

    def is_read(self) -> bool:
        return self.was_read

    async def reply(self, content: str, schema: Optional[str] = None) -> Optional[Message]:
        if schema is None:
            schema = self.SCHEMA

        content = content.format(message=self)
        subject = schema.format(message=self)

        return await self.user.send(subject, content)

    async def read(self) -> str:
        if self.has_content():
            return self.content

        message = await self.client.get_message(self, self.type)

        if message.has_content():
            content = message.content

            self.content = content

            return content

        raise ClientError(READ_FAILED)
