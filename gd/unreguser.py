from .abstractentity import AbstractEntity

class UnregisteredUser(AbstractEntity):
    def __init__(self):
        super().__init__()
        self._name = 'UnregisteredUser'
    
    def __str__(self):
        res = f'[gd.UnregisteredUser]\n[ID:{self.id}]'
        return res
    
    def __repr__(self):
        ret = f'<gd.UnregisteredUser: id={self.id}>'
        return ret
        
    @property
    def name(self):
        return self._name