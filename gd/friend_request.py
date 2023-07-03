from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar

from attrs import define, field
from pendulum import DateTime

from gd.binary import VERSION, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS, DEFAULT_ID, DEFAULT_READ, EMPTY
from gd.date_time import utc_from_timestamp, utc_now
from gd.entity import Entity
from gd.enums import ByteOrder, FriendRequestType
from gd.models import FriendRequestModel
from gd.users import User, UserCosmetics

if TYPE_CHECKING:
    from gd.client import Client

__all__ = ("FriendRequest",)

FR = TypeVar("FR", bound="FriendRequest")

FRIEND_REQUEST = "{} {}"
friend_request = FRIEND_REQUEST.format

INCOMING = "<-"
OUTGOING = "->"

READ_BIT = 0b00000010
TYPE_MASK = 0b00000001


@define()
class FriendRequest(Entity):
    user: User = field(eq=False)
    type: FriendRequestType = field(eq=False)

    created_at: DateTime = field(factory=utc_now, eq=False)

    content: str = field(default=EMPTY, eq=False)

    was_read: bool = field(default=DEFAULT_READ, eq=False)

    @classmethod
    def from_binary(
        cls: Type[FR],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> FR:
        read_bit = READ_BIT

        reader = Reader(binary, order)

        id = reader.read_u32()

        user = User.from_binary(binary, order, version, encoding, errors)

        value = reader.read_u8()

        type_value = value & TYPE_MASK

        type = FriendRequestType(type_value)

        was_read = value & read_bit == read_bit

        timestamp = reader.read_f64()

        created_at = utc_from_timestamp(timestamp)

        content_length = reader.read_u8()

        content = reader.read(content_length).decode(encoding, errors)

        return cls(
            id=id, user=user, type=type, created_at=created_at, content=content, was_read=was_read
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

        self.user.to_binary(binary, order, version, encoding, errors)

        value = self.type.value

        if self.is_read():
            value |= READ_BIT

        writer.write_u8(value)

        timestamp = self.created_at.timestamp()  # type: ignore

        writer.write_f64(timestamp)

        data = self.content.encode(encoding, errors)

        writer.write_u8(len(data))

        writer.write(data)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return friend_request(self.direction, self.user)

    @property
    def direction(self) -> str:
        return INCOMING if self.is_incoming() else OUTGOING

    @classmethod
    def default(
        cls: Type[FR],
        id: int = DEFAULT_ID,
        user_id: int = DEFAULT_ID,
        user_account_id: int = DEFAULT_ID,
    ) -> FR:
        return cls(
            id=id, user=User.default(user_id, user_account_id), type=FriendRequestType.DEFAULT
        )

    @classmethod
    def from_model(cls: Type[FR], model: FriendRequestModel, type: FriendRequestType) -> FR:
        return cls(
            id=model.id,
            user=User(
                name=model.name,
                id=model.user_id,
                account_id=model.account_id,
                cosmetics=UserCosmetics(
                    color_1_id=model.color_1_id,
                    color_2_id=model.color_2_id,
                    icon_type=model.icon_type,
                    icon_id=model.icon_id,
                    glow=model.glow,
                ),
            ),
            type=type,
            created_at=model.created_at,
            content=model.content,
            was_read=model.read,
        )

    async def read(self) -> None:
        await self.client.read_friend_request(self)

    async def delete(self) -> None:
        await self.client.delete_friend_request(self)

    async def accept(self) -> None:
        await self.client.accept_friend_request(self)

    def is_read(self) -> bool:
        return self.was_read

    def is_unread(self) -> bool:
        return not self.was_read

    def is_incoming(self) -> bool:
        return self.type.is_incoming()

    def is_outgoing(self) -> bool:
        return self.type.is_outgoing()

    def attach_client_unchecked(self: FR, client: Optional[Client]) -> FR:
        self.user.attach_client_unchecked(client)

        return super().attach_client_unchecked(client)

    def attach_client(self: FR, client: Client) -> FR:
        self.user.attach_client(client)

        return super().attach_client(client)

    def detach_client(self: FR) -> FR:
        self.user.detach_client()

        return super().detach_client()
