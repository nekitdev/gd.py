from __future__ import annotations

from builtins import getattr as get_attribute
from builtins import setattr as set_attribute
from typing import TYPE_CHECKING, Any

from attrs import Attribute, define, field, fields
from iters.iters import iter
from typing_aliases import Unary
from typing_extensions import Self
from wraps.option import NULL, Option, Some

from gd.converters import CONVERTER, register_unstructure_hook_omit_client
from gd.defaults.entities.core import DEFAULT_ID
from gd.typing import Data

if TYPE_CHECKING:
    from gd.clients import Client

else:
    Client = Any  # use `Any` since we can not import `Client`, mostly for `cattrs` code generation

__all__ = ("Entity", "EntityData")

EXPECTED_ID = "expected non-negative ID"
EXPECTED_CLIENT = "expected client"


class EntityData(Data):
    id: int


def attribute_name(attribute: Attribute[Any]) -> str:
    return attribute.name


def copy_attribute(self: Any, entity: Any, name: str) -> None:
    set_attribute(self, name, get_attribute(entity, name))


def copy_attribute_factory(self: Any, entity: Any) -> Unary[str, None]:
    def copy(name: str) -> None:
        copy_attribute(self, entity, name)

    return copy


@register_unstructure_hook_omit_client
@define()
class Entity:
    """Represents entities."""

    id: int = field()
    """The ID of the entity."""

    client: Option[Client] = field(default=NULL, init=False, repr=False, eq=False)
    """The client of the entity; [`Some(client)`][wraps.option.Some] if the client is attached,
    [`NULL`][wraps.option.NULL] otherwise.
    """

    @classmethod
    def default(cls, id: int = DEFAULT_ID) -> Self:
        return cls(id=id)

    @id.validator
    def check_id(self, attribute: Attribute[int], id: int) -> None:
        if id < 0:
            raise ValueError(EXPECTED_ID)

    @property
    def client_expected(self) -> Client:
        """The expected client of the entity; panics if no client is attached."""
        return self.client.expect(EXPECTED_CLIENT)

    def attach_option(self, option: Option[Client]) -> Self:
        """Attaches the client `option` to the entity.

        This is equivalent to:

        ```python
        entity.client = option
        ```

        Arguments:
            option: The client option to attach.

        Returns:
            The entity with the client option attached.
        """
        self.client = option

        return self

    def attach_client(self, client: Client) -> Self:
        """Attaches the `client` to the entity.

        This is equivalent to:

        ```python
        entity.attach_option(Some(client))
        ```

        Arguments:
            client: The client to attach.

        Returns:
            The entity with the client attached.
        """
        return self.attach_option(Some(client))

    def detach_client(self) -> Self:
        """Detaches the `client` from the entity.

        This is equivalent to:

        ```python
        entity.attach_option(NULL)
        ```

        Returns:
            The entity with the client detached.
        """
        return self.attach_option(NULL)

    def update_from(self, entity: Entity) -> Self:
        iter(fields(type(entity))).map(attribute_name).for_each(
            copy_attribute_factory(self, entity)
        )

        return self

    @classmethod
    def from_data(cls, data: EntityData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> EntityData:
        return CONVERTER.unstructure(self)  # type: ignore
