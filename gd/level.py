from .abstractentity import AbstractEntity

class Level(AbstractEntity):
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options