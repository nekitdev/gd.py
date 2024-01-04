from __future__ import annotations

from io import BufferedReader, BufferedWriter
from typing import TYPE_CHECKING, ClassVar, Optional

from attrs import define, field
from pendulum import DateTime

from gd.binary import Binary
from gd.constants import DEFAULT_READ, EMPTY
from gd.date_time import (
    timestamp_milliseconds,
    utc_from_timestamp_milliseconds,
    utc_now,
)
from gd.entity import Entity
from gd.enums import MessageType
from gd.errors import ClientError
from gd.schema import MessageSchema
from gd.schema_constants import NONE
from gd.users import UserReference

if TYPE_CHECKING:
    from typing_extensions import Self

    from gd.client import Client
    from gd.models import MessageModel
    from gd.schema import MessageBuilder, MessageReader

__all__ = ("Message", "MessageReference")


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


READ_FAILED = "failed to read message (no content)"


@define()
class Message(Binary, MessageReference):
    SCHEMA: ClassVar[str] = "Re: {message.subject}"

    created_at: DateTime = field(factory=utc_now, eq=False)

    subject: str = field(default=EMPTY, eq=False)
    content: Optional[str] = field(default=None, eq=False)

    was_read: bool = field(default=DEFAULT_READ, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return self.subject

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(MessageSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(MessageSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with MessageSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(MessageSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: MessageReader) -> Self:
        option = reader.content

        if option.which() == NONE:
            content = None

        else:
            content = option.some

        return cls(
            id=reader.id,
            user=UserReference.from_reader(reader.user),
            type=MessageType(reader.type),
            created_at=utc_from_timestamp_milliseconds(reader.createdAt),
            subject=reader.subject,
            content=content,
            was_read=reader.read,
        )

    def to_builder(self) -> MessageBuilder:
        builder = MessageSchema.new_message()

        builder.id = self.id
        builder.user = self.user.to_builder()
        builder.type = self.type.value
        builder.createdAt = timestamp_milliseconds(self.created_at)
        builder.subject = self.subject

        content = self.content

        if content is None:
            builder.content.none = None

        else:
            builder.content.some = content

        builder.read = self.is_read()

        return builder

    @classmethod
    def from_model(cls, model: MessageModel) -> Self:
        type = MessageType.OUTGOING if model.is_sent() else MessageType.INCOMING

        return cls(
            id=model.id,
            user=UserReference(id=model.user_id, name=model.name, account_id=model.account_id),
            type=type,
            created_at=model.created_at,
            subject=model.subject,
            content=model.content,
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
        content = self.content

        if content is None:
            message = await self.client.get_message(self)

            content = message.content

            if content is None:
                raise ClientError(READ_FAILED)

            self.content = content

        return content

    def as_reference(self) -> MessageReference:
        return MessageReference(id=self.id, user=self.user, type=self.type)
