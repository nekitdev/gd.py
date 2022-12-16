from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Optional, Type, TypeVar

from attrs import define, field

from gd.constants import DEFAULT_READ, EMPTY
from gd.date_time import DateTime, utc_from_timestamp, utc_now
from gd.entity import Entity
from gd.enums import MessageType
from gd.models import MessageModel
from gd.users import User

if TYPE_CHECKING:
    from gd.client import Client

__all__ = ("Message",)

M = TypeVar("M", bound="Message")


@define()
class Message(Entity):
    SCHEMA: ClassVar[str] = "Re: {message.subject}"

    user: User = field(eq=False)
    type: MessageType = field(eq=False)

    created_at: DateTime = field(factory=utc_now, eq=False)

    subject: str = field(default=EMPTY, eq=False)
    content: Optional[str] = field(default=None, eq=False)

    was_read: bool = field(default=DEFAULT_READ, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return self.subject

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
            content=model.content if model.is_content_present() else None,
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
