from attrs import define, field

from gd.entity import Entity
from gd.enums import RelationshipType
from gd.user import User

__all__ = ("Relationship",)


@define()
class Relationship(Entity):
    user: User = field()
    type: RelationshipType = field()

    id: int = field()

    @id.default
    def default_id(self) -> int:
        return self.user.id
