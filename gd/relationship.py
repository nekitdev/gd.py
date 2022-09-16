from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypeVar

from attrs import define, field

from gd.entity import Entity
from gd.enums import RelationshipType

if TYPE_CHECKING:
    from gd.client import Client
    from gd.user import User

__all__ = ("Relationship",)

R = TypeVar("R", bound="Relationship")


@define(hash=True)
class Relationship(Entity):
    user: User = field(eq=False)
    type: RelationshipType = field(eq=False)

    id: int = field()

    @id.default
    def default_id(self) -> int:
        return self.user.id

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def maybe_attach_client(self: R, client: Optional[Client]) -> R:
        self.user.maybe_attach_client(client)

        return super().maybe_attach_client(client)

    def attach_client(self: R, client: Client) -> R:
        self.user.attach_client(client)

        return super().attach_client(client)

    def detach_client(self: R) -> R:
        self.user.detach_client()

        return super().detach_client()
