from gd.decorators import synchronize
from gd.errors import ClientException
from gd.model import Model  # type: ignore
from gd.text_utils import make_repr
from gd.typing import TYPE_CHECKING, Any, Dict, Optional, Type, TypeVar

__all__ = ("AbstractEntity",)

AbstractEntityT = TypeVar("AbstractEntityT", bound="AbstractEntity")

DATA_IGNORE = {"client"}

if TYPE_CHECKING:
    from gd.client import Client


@synchronize
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

    def __init__(self, *, client: Optional["Client"] = None, **options) -> None:
        self.options = options
        self.attach_client(client)

    def __repr__(self) -> str:
        info = {"id": self.id}
        return make_repr(self, info)

    def __hash__(self) -> int:
        return hash(self.hash_str)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.id == other.id

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.id != other.id

    def __json__(self) -> Dict[str, Any]:
        return self.to_dict()

    def update_inner(self: AbstractEntityT, **options: Any) -> AbstractEntityT:
        """Update ``self.options`` with ``options``."""
        self.options.update(options)
        return self

    @classmethod
    def from_model(cls: Type[AbstractEntityT], model: Model, *args, **kwargs) -> AbstractEntityT:
        """Create new entity from given ``model``, ``args`` and ``kwargs``."""
        raise NotImplementedError

    @classmethod
    def from_models(cls: Type[AbstractEntityT], *models: Model, **kwargs) -> AbstractEntityT:
        """Create new entity from given ``models`` by calling ``from_model`` with ``kwargs``."""
        self = cls()

        for model in models:
            self.options.update(cls.from_model(model, **kwargs).options)

        return self

    @classmethod
    def from_dicts(
        cls: Type[AbstractEntityT],
        *data: Dict[str, Any],
        client: Optional["Client"] = None,
        **kwargs,
    ) -> AbstractEntityT:
        """Create new entity from dictionaries in ``data``, with ``client`` and ``kwargs``."""
        self = cls(client=client)

        for part in data:
            self.options.update(part)

        self.options.update(kwargs)

        return self

    from_dict = from_dicts

    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary."""
        return {key: value for key, value in self.options.items() if key not in DATA_IGNORE}

    @property
    def hash_str(self) -> str:
        """:class:`str`: String used for hashing, with format ``<Class(ID->id)>``."""
        return f"<{self.__class__.__name__}(ID->{self.id})>"

    @property
    def id(self) -> int:
        """:class:`int`: ID of the Entity."""
        return self.options.get("id", 0)

    @property
    def client(self) -> "Client":
        """:class:`~gd.Client`: Client attached to this object.
        This checks if client is not present, and raises :class:`~gd.ClientException` in that case.
        """
        client = self.client_unchecked

        if client is None:
            raise ClientException(f"Client is not attached to an entity: {self!r}.")

        return client

    @property
    def client_unchecked(self) -> Optional["Client"]:
        """Optional[:class:`~gd.Client`]: Client attached to this object."""
        return self.options.get("client")

    def attach_client(self: AbstractEntityT, client: Optional["Client"] = None) -> AbstractEntityT:
        """Attach ``client`` to ``self``.

        Parameters
        ----------
        client: Optional[:class:`gd.Client`]
            Client to attach. If ``None`` or not given, will be detached.

        Returns
        -------
        :class:`~gd.AbstractEntity`
            This abstract entity.
        """
        self.options.update(client=client)

        return self

    def detach_client(self: AbstractEntityT) -> AbstractEntityT:
        """Detach ``client`` from ``self``.

        Same as calling::

            self.attach_client(None)

        Returns
        -------
        :class:`~gd.AbstractEntity`
            This abstract entity.
        """
        self.attach_client(None)

        return self
