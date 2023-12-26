from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from gd.constants import DEFAULT_ID, DEFAULT_READ, EMPTY
from gd.date_time import utc_now
from gd.entity import Entity
from gd.enums import FriendRequestType
from gd.users import User, UserCosmetics

if TYPE_CHECKING:
    from pendulum import DateTime
    from typing_extensions import Self

    from gd.client import Client
    from gd.models import FriendRequestModel

__all__ = ("FriendRequest",)

FRIEND_REQUEST = "{} {}"
friend_request = FRIEND_REQUEST.format

INCOMING = "<-"
OUTGOING = "->"


@define()
class FriendRequest(Entity):
    user: User = field(eq=False)
    type: FriendRequestType = field(eq=False)

    created_at: DateTime = field(factory=utc_now, eq=False)

    content: str = field(default=EMPTY, eq=False)

    was_read: bool = field(default=DEFAULT_READ, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return friend_request(self.direction, self.user)

    @property
    def direction(self) -> str:
        return INCOMING if self.is_incoming() else OUTGOING

    @classmethod
    def default(
        cls,
        id: int = DEFAULT_ID,
        user_id: int = DEFAULT_ID,
        user_account_id: int = DEFAULT_ID,
    ) -> Self:
        return cls(
            id=id, user=User.default(user_id, user_account_id), type=FriendRequestType.DEFAULT
        )

    @classmethod
    def from_model(cls, model: FriendRequestModel, type: FriendRequestType) -> Self:
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

    def attach_client_unchecked(self, client: Optional[Client]) -> Self:
        self.user.attach_client_unchecked(client)

        return super().attach_client_unchecked(client)

    def attach_client(self, client: Client) -> Self:
        self.user.attach_client(client)

        return super().attach_client(client)

    def detach_client(self) -> Self:
        self.user.detach_client()

        return super().detach_client()
