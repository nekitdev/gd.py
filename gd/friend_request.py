from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Type, TypeVar

from attrs import define, field

from gd.constants import DEFAULT_ID, DEFAULT_READ, EMPTY
from gd.entity import Entity
from gd.enums import FriendRequestType
from gd.models import FriendRequestModel
from gd.relationship import Relationship
from gd.users import User

if TYPE_CHECKING:
    from gd.client import Client

__all__ = ("FriendRequest",)

FR = TypeVar("FR", bound="FriendRequest")


@define()
class FriendRequest(Entity):
    user: User = field(eq=False)
    type: FriendRequestType = field(eq=False)

    created_at: datetime = field(factory=datetime.utcnow, eq=False)

    content: str = field(default=EMPTY, eq=False)

    was_read: bool = field(default=DEFAULT_READ, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return self.content

    @classmethod
    def default(cls: Type[FR]) -> FR:
        return cls(id=DEFAULT_ID, user=User.default(), type=FriendRequestType.DEFAULT)

    @classmethod
    def from_model(cls: Type[FR], model: FriendRequestModel, type: FriendRequestType) -> FR:
        return cls(
            id=model.id,
            user=User(
                name=model.name,
                id=model.user_id,
                icon_id=model.icon_id,
                color_1_id=model.color_1_id,
                color_2_id=model.color_2_id,
                icon_type=model.icon_type,
                glow=model.glow,
                account_id=model.account_id,
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

    def into_relationship(self) -> Relationship:
        return Relationship(
            id=self.id, user=self.user, type=self.type.into_relationship_type()
        ).attach_client_unchecked(self.client_unchecked)

    def attach_client_unchecked(self: FR, client: Optional[Client]) -> FR:
        self.user.attach_client_unchecked(client)

        return super().attach_client_unchecked(client)

    def attach_client(self: FR, client: Client) -> FR:
        self.user.attach_client(client)

        return super().attach_client(client)

    def detach_client(self: FR) -> FR:
        self.user.detach_client()

        return super().detach_client()
