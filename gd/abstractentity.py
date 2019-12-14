from .utils.wrap_tools import make_repr

class AbstractEntity:
    """Class that represents Abstract Entity. This is a base for many gd.py objects.

    .. container:: operations

        .. describe:: x == y

            Check if two objects are equal. Compared by hash and type.

        .. describe:: x != y

            Check if two objects are not equal.

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
        return hash(self.hash_str)

    def __eq__(self, other):
        if not hasattr(other, 'id'):
            return False
        return type(self) == type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def hash_str(self):
        cls = self.__class__.__name__
        return '<GDEntity<{}(ID->{})>>'.format(cls, self.id)

    @property
    def id(self):
        """:class:`int`: ID of the Entity."""
        return self.options.get('id', 0)

    def attach_client(self, client):
        self._client = client
        return self
