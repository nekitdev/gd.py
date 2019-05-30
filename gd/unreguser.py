from .abstractentity import AbstractEntity

class UnregisteredUser(AbstractEntity):
    def __init__(self):
        super().__init__()
        self._name = 'UnregisteredUser'
    
    def __str__(self):
        res = f'[UnregisteredUser]\n[ID:{self.id}]'
        return res
    
    @property
    def name(self):
        return self._name