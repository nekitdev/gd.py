from .utils.wrap_tools import make_repr

class AbstractEntity:
    """Class that represents Abstract Entity. This is a base for many gd.py objects.

    .. container:: operations

        .. describe:: x == y

            Check if two objects are equal. Compared by hash and type.

        .. describe:: x != y

            Check if two objects are not equal

        .. describe:: hash(x)

            Returns ``hash(self.to_hash_string())``.
    """
    def __init__(self, **options):
        self.options = options
        self._client = options.get('client')  # None if not provided

    def __repr__(self):
        info = {'id': self.id}
        return make_repr(self, info)

    def __hash__(self):
        return hash(self.to_hash_string())

    def __eq__(self, other):
        return isinstance(other, type(self)) and hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def id(self):
        """:class:`int`: ID of the Entity."""
        return self.options.get('id', 0)

    def to_hash_string(self):
        """:class:`str`: Converts to a string which is used in ``hash(self)``."""
        cls = self.__class__.__name__
        id = self.id
        r = self.__repr__()

        hash_string = '<GDEntity<{cls}>[id={id};repr={r}]>'.format(cls=cls, id=id, r=r)

        return hash_string

    def attach_client(self, client):
        self._client = client
        return self
