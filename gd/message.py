from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Optional, Type, TypeVar

from attrs import define, field

from gd.binary import VERSION, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS, DEFAULT_READ, EMPTY
from gd.date_time import DateTime, utc_from_timestamp, utc_now
from gd.entity import Entity
from gd.enums import ByteOrder, MessageType
from gd.models import MessageModel
from gd.users import User

if TYPE_CHECKING:
    from gd.client import Client

__all__ = ("Message",)

M = TypeVar("M", bound="Message")

CONTENT_BIT = 0b00000100
READ_BIT = 0b00000010
TYPE_MASK = 0b00000001

NO_SUBJECT = "(no subject)"


@define()
class Message(Entity):
    SCHEMA: ClassVar[str] = "Re: {message.subject}"

    user: User = field(eq=False)
    type: MessageType = field(eq=False)

    created_at: DateTime = field(factory=utc_now, eq=False)

    subject: str = field(default=EMPTY, eq=False)
    content: Optional[str] = field(default=None, eq=False)

    was_read: bool = field(default=DEFAULT_READ, eq=False)

    @classmethod
    def from_binary(
        cls: Type[M],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> M:
        read_bit = READ_BIT
        content_bit = CONTENT_BIT

        reader = Reader(binary, order)

        id = reader.read_u32()

        user = User.from_binary(binary, order, version, encoding, errors)

        value = reader.read_u8()

        type_value = value & TYPE_MASK

        type = MessageType(type_value)

        was_read = value & read_bit == read_bit

        has_content = value & content_bit == content_bit

        subject_length = reader.read_u8()

        subject = reader.read(subject_length).decode(encoding, errors)

        if has_content:
            content_length = reader.read_u8()

            content = reader.read(content_length).decode(encoding, errors)

        else:
            content = None

        timestamp = reader.read_f64()

        created_at = utc_from_timestamp(timestamp)

        return cls(
            id=id,
            user=user,
            type=type,
            created_at=created_at,
            subject=subject,
            content=content,
            was_read=was_read,
        )

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        super().to_binary(binary, order, version)

        writer = Writer(binary, order)

        content = self.content

        value = self.type.value

        if self.is_read():
            value |= READ_BIT

        if content is not None:
            value |= CONTENT_BIT

        writer.write_u8(value)

        data = self.subject.encode(encoding, errors)

        writer.write_u8(len(data))
        writer.write(data)

        if content is not None:
            data = content.encode(encoding, errors)

            writer.write_u8(len(data))
            writer.write(data)

        timestamp = self.created_at.timestamp()  # type: ignore

        writer.write_f64(timestamp)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return self.subject or NO_SUBJECT

    def is_incoming(self) -> bool:
        return self.type.is_incoming()

    def is_outgoing(self) -> bool:
        return self.type.is_outgoing()

    @classmethod
    def from_model(cls: Type[M], model: MessageModel) -> M:
        type = MessageType.OUTGOING if model.is_sent() else MessageType.INCOMING

        return cls(
            id=model.id,
            user=User(id=model.user_id, name=model.name, account_id=model.account_id),
            type=type,
            created_at=model.created_at,
            subject=model.subject,
            content=model.content if model.has_content() else None,
            was_read=model.read,
        )

    @property
    def body(self) -> Optional[str]:
        return self.content

    def is_read(self) -> bool:
        return self.was_read

    async def read(self) -> str:
        content = self.content

        if content is None:
            message = await self.client.get_message(self.id, self.type)

            self.content = content = message.content

        return content  # type: ignore

    async def reply(self, content: str, schema: Optional[str] = None) -> Optional[Message]:
        if schema is None:
            schema = self.SCHEMA

        content = content.format(message=self)
        subject = schema.format(message=self)

        return await self.user.send(subject, content)

    async def delete(self) -> None:
        await self.client.delete_message(self)

    def attach_client_unchecked(self: M, client: Optional[Client]) -> M:
        self.user.attach_client_unchecked(client)

        return super().attach_client_unchecked(client)

    def attach_client(self: M, client: Client) -> M:
        self.user.attach_client(client)

        return super().attach_client(client)

    def detach_client(self: M) -> M:
        self.user.detach_client()

        return super().detach_client()
