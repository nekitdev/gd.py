from __future__ import annotations

from builtins import getattr as get_attribute
from builtins import setattr as set_attribute
from typing import TYPE_CHECKING, Any, Optional, TypeVar

from attrs import Attribute, define, field, fields
from iters.iters import iter
from typing_extensions import Self
from gd.constants import DEFAULT_ID

from gd.converter import CONVERTER, register_unstructure_hook_omit_client
from gd.defaults import Default
from gd.errors import ClientError
from gd.typing import Data

if TYPE_CHECKING:
    from gd.client import Client

else:
    Client = Any

__all__ = ("Entity", "EntityData")

E = TypeVar("E", bound="Entity")

CLIENT_NOT_ATTACHED = "`client` not attached to the entity: {}"


class EntityData(Data):
    id: int


def attribute_name(attribute: Attribute[Any]) -> str:
    return attribute.name


@register_unstructure_hook_omit_client
@define()
class Entity(Default):
    id: int = field()

    client_unchecked: Optional[Client] = field(default=None, init=False, repr=False, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @classmethod
    def default(cls, id: int = DEFAULT_ID) -> Self:
        return cls(id=id)

    @id.validator
    def check_id(self, attribute: Attribute[int], id: int) -> None:
        if id < 0:
            raise ValueError  # TODO: message?

    @property
    def client(self) -> Client:
        result = self.client_unchecked

        if result is None:
            raise ClientError(CLIENT_NOT_ATTACHED.format(self))

        return result

    @client.setter
    def client(self, client: Client) -> None:
        self.client_unchecked = client

    @client.deleter
    def client(self) -> None:
        self.client_unchecked = None

    def attach_client_unchecked(self, client: Optional[Client]) -> Self:
        self.client_unchecked = client

        return self

    def attach_client(self, client: Client) -> Self:
        self.client = client

        return self

    def detach_client(self) -> Self:
        del self.client

        return self

    def update_from(self, entity: Entity) -> Self:
        for name in iter(fields(type(entity))).map(attribute_name).unwrap():
            set_attribute(self, name, get_attribute(entity, name))

        return self

    @classmethod
    def from_data(cls, data: EntityData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> EntityData:
        return CONVERTER.unstructure(self)  # type: ignore
