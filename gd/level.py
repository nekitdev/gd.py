from .abstractentity import AbstractEntity
from .utils.wrap_tools import _make_repr

class Level(AbstractEntity):
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options