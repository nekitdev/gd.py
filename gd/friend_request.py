from attrs import define

from gd.constants import EMPTY
from gd.entity import Entity
from gd.enums import FriendRequestType
from gd.relationship import Relationship
# from gd.models import FriendRequestModel
from gd.user import User

__all__ = ("FriendRequest",)


@define()
class FriendRequest(Entity):
    user: User
    type: FriendRequestType

    was_read: bool = False
    content: str = EMPTY

    def __str__(self) -> str:
        return self.content

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

    def into_relationship(self) -> Relationship:
        return Relationship(
            id=self.id, user=self.user, type=self.type.into_relationship_type()
        ).maybe_attach_client(self.maybe_client)
