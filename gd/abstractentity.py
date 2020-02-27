from .typing import AbstractEntity, Client
from .errors import ClientException
from .utils.text_tools import make_repr


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
    def __init__(self, **options) -> None:
        self.options = options
        self._client = options.get('client')  # None if not provided

    def __repr__(self) -> str:
        info = {'id': self.id}
        return make_repr(self, info)

    def __str__(self) -> str:
        return self.hash_str

    def __hash__(self) -> int:
        return hash(self.hash_str)

    def __eq__(self, other: AbstractEntity) -> bool:
        if not hasattr(other, 'id'):
            return False
        return type(self) == type(other) and self.id == other.id

    def __ne__(self, other: AbstractEntity) -> bool:
        return not self.__eq__(other)

    def _json(self) -> dict:  # pragma: no cover
        return self.options

    @property
    def hash_str(self) -> str:
        cls = self.__class__.__name__
        return '<GDEntity<{}(ID->{})>>'.format(cls, self.id)

    @property
    def id(self) -> int:
        """:class:`int`: ID of the Entity."""
        return self.options.get('id', 0)

    @property
    def client(self) -> Client:
        """:class:`.Client`: Client attached to this object."""
        if self._client is None:
            raise ClientException('Client is not attached to the entity: {!r}.'.format(self))
        return self._client

    def attach_client(self, client: Client) -> None:
        """Attach ``client`` to ``self``."""
        self._client = client
        return self
