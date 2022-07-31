from attrs import define

from gd.entity import Entity
from gd.enums import RelationshipType
from gd.user import User

__all__ = ("Relationship",)


@define()
class Relationship(Entity):
    user: User
    type: RelationshipType
