from gd.typing import AbstractEntity, Any, Client, Dict, Iterable
from gd.errors import ClientException

from gd.utils.decorators import impl_sync
from gd.utils.parser import ExtDict
from gd.utils.text_tools import make_repr


@impl_sync
class AbstractEntity:
    """Class that represents Abstract Entity. This is a base for many gd.py objects.

    .. container:: operations

        .. describe:: x == y

            Check if two objects are equal. Compared by hash and type.

        .. describe:: x != y

            Check if two objects are not equal.

        .. describe:: hash(x)

            Returns ``hash(self.hash_str)``.
    """

    def __init__(self, *, client: Client = None, **options) -> None:
        self.options = options
        self.attach_client(client)

    def __repr__(self) -> str:
        info = {"id": self.id}
        return make_repr(self, info)

    def __hash__(self) -> int:
        return hash(self.hash_str)

    def __eq__(self, other: AbstractEntity) -> bool:
        if not hasattr(other, "id"):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other: AbstractEntity) -> bool:
        if not hasattr(other, "id"):
            return NotImplemented
        return type(self) is not type(other) or self.id != other.id

    def __json__(self, ignore: Iterable[str] = {"client", "data"}) -> Dict[str, Any]:
        return {key: value for key, value in self.options.items() if key not in ignore}

    @classmethod
    def from_data(cls, data: ExtDict, client: Client) -> AbstractEntity:
        return cls(client=client)

    @property
    def hash_str(self) -> str:
        name = self.__class__.__name__
        return f"<GDEntity<{name}(ID->{self.id})>>"

    @property
    def id(self) -> int:
        """:class:`int`: ID of the Entity."""
        return self.options.get("id", 0)

    @property
    def client(self) -> Client:
        """:class:`.Client`: Client attached to this object."""
        client = self.options.get("client")

        if client is None:
            raise ClientException(f"Client is not attached to an entity: {self!r}.")

        return client

    def attach_client(self, client: Client) -> None:
        """Attach ``client`` to ``self``."""
        self.options.update(client=client)
        return self
