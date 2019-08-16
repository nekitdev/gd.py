from .abstractentity import AbstractEntity
from .utils.wrap_tools import make_repr

class UnregisteredUser(AbstractEntity):
    """Class that represents Unregistered Users in Geometry Dash.
    This class is derived from :class:`.AbstractEntity`.

    .. note::

        ID of :class:`.UnregisteredUser` objects always equals ``0``.

    """
    def __init__(self):
        super().__init__()
        self._name = 'UnregisteredUser'
    
    def __repr__(self):
        info = {'id': self.id}
        return make_repr(self, info)
        
    @property
    def name(self):
        """:class:`str`: A name of the user. (*'UnregisteredUser'*)"""
        return self._name