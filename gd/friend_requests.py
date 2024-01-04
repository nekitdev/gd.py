from __future__ import annotations

from io import BufferedReader, BufferedWriter
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from gd.binary import Binary
from gd.constants import DEFAULT_ID, DEFAULT_READ, EMPTY
from gd.date_time import (
    timestamp_milliseconds,
    utc_from_timestamp_milliseconds,
    utc_now,
)
from gd.entity import Entity
from gd.enums import FriendRequestType
from gd.schema import FriendRequestSchema
from gd.users import UserReference

if TYPE_CHECKING:
    from pendulum import DateTime
    from typing_extensions import Self

    from gd.client import Client
    from gd.models import FriendRequestModel
    from gd.schema import FriendRequestBuilder, FriendRequestReader

__all__ = ("FriendRequest", "FriendRequestReference")

FRIEND_REQUEST = "{} {}"
friend_request = FRIEND_REQUEST.format

INCOMING = "<-"
OUTGOING = "->"


@define()
class FriendRequestReference(Entity):
    user: UserReference = field(eq=False)
    type: FriendRequestType = field(eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return friend_request(self.direction, self.user)

    @classmethod
    def default(
        cls,
        id: int = DEFAULT_ID,
        user_id: int = DEFAULT_ID,
        user_account_id: int = DEFAULT_ID,
        type: FriendRequestType = FriendRequestType.DEFAULT,
    ) -> Self:
        return cls(
            id=id,
            user=UserReference.default(user_id, user_account_id),
            type=FriendRequestType.DEFAULT,
        )

    def is_incoming(self) -> bool:
        return self.type.is_incoming()

    def is_outgoing(self) -> bool:
        return self.type.is_outgoing()

    @property
    def direction(self) -> str:
        return INCOMING if self.is_incoming() else OUTGOING

    def attach_client_unchecked(self, client: Optional[Client]) -> Self:
        self.user.attach_client_unchecked(client)

        return super().attach_client_unchecked(client)

    def attach_client(self, client: Client) -> Self:
        self.user.attach_client(client)

        return super().attach_client(client)

    def detach_client(self) -> Self:
        self.user.detach_client()

        return super().detach_client()

    async def read(self) -> None:
        await self.client.read_friend_request(self)

    async def delete(self) -> None:
        await self.client.delete_friend_request(self)

    async def accept(self) -> None:
        await self.client.accept_friend_request(self)


NO_CONTENT = "no content"


@define()
class FriendRequest(Binary, FriendRequestReference):
    created_at: DateTime = field(factory=utc_now, eq=False)

    content: str = field(default=EMPTY, eq=False)

    was_read: bool = field(default=DEFAULT_READ, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @classmethod
    def from_model(cls, model: FriendRequestModel, type: FriendRequestType) -> Self:
        return cls(
            id=model.id,
            user=UserReference(name=model.name, id=model.user_id, account_id=model.account_id),
            type=type,
            created_at=model.created_at,
            content=model.content,
            was_read=model.read,
        )

    def is_read(self) -> bool:
        return self.was_read

    def is_unread(self) -> bool:
        return not self.was_read

    def as_reference(self) -> FriendRequestReference:
        return FriendRequestReference(id=self.id, user=self.user, type=self.type)

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(FriendRequestSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(FriendRequestSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with FriendRequestSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(FriendRequestSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: FriendRequestReader) -> Self:
        return cls(
            id=reader.id,
            user=UserReference.from_reader(reader.user),
            type=FriendRequestType(reader.type),
            created_at=utc_from_timestamp_milliseconds(reader.createdAt),
            content=reader.content,
            was_read=reader.read,
        )

    def to_builder(self) -> FriendRequestBuilder:
        builder = FriendRequestSchema.new_message()

        builder.id = self.id
        builder.user = self.user.to_builder()
        builder.type = self.type.value
        builder.createdAt = timestamp_milliseconds(self.created_at)
        builder.content = self.content
        builder.read = self.is_read()

        return builder
