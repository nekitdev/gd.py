from .utils.wrap_tools import make_repr

class AbstractEntity:
    """Class that represents Abstract Entity. This is a base for many gd.py objects."""
    def __init__(self, **options):
        self._id = options.get('id', 0)
        self._client = None  # let's leave it like this on init

    def __repr__(self):
        info = {'id': self.id}
        return make_repr(self, info)
    
    @property
    def id(self):
        """:class:`int`: ID of the Entity."""
        return self._id

    def _attach_client(self, client):
        self._client = client
        return self
