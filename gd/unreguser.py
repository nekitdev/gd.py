from .abstractentity import AbstractEntity
from .utils.wrap_tools import _make_repr

class UnregisteredUser(AbstractEntity):
    def __init__(self):
        super().__init__()
        self._name = 'UnregisteredUser'
    
    def __repr__(self):
        info = {'id': self.id}
        return _make_repr(self, info)
        
    @property
    def name(self):
        return self._name