from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from attrs import define, field

from gd.entity import Entity
from gd.enums import RelationshipType

if TYPE_CHECKING:
    from gd.client import Client
    from gd.user import User

__all__ = ("Relationship",)

R = TypeVar("R", bound="Relationship")


@define()
class Relationship(Entity):
    user: User = field()
    type: RelationshipType = field()

    id: int = field()

    @id.default
    def default_id(self) -> int:
        return self.user.id

    def attach_client(self: R, client: Client) -> R:
        self.user.attach_client(client)

        return super().attach_client(client)
