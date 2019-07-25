from .utils.wrap_tools import _make_repr

class AbstractEntity:
    def __init__(self, **options):
        self._id = options.get('id', 0)
    
    def __repr__(self):
        info = {'id': self.id}
        return _make_repr(self, info)
    
    @property
    def id(self):
        return self._id