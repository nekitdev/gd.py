from .abstractentity import AbstractEntity
from .utils.wrap_tools import make_repr

class UnregisteredUser(AbstractEntity):
    """Class that represents Unregistered Users in Geometry Dash.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __init__(self, id: int = 0, name: str = 'UnregisteredUser'):
        super().__init__(id=id)
        self._name = name

    def __repr__(self):
        info = {'id': self.id, 'name': self.name}
        return make_repr(self, info)

    @property
    def name(self):
        """:class:`str`: A name of the user. ``'UnregisteredUser'`` if not present."""
        return self._name
