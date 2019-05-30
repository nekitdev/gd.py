from .abstractentity import AbstractEntity

class AbstractUser(AbstractEntity):
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
    
    def __str__(self):
        ret = f"[gd.AbstractUser]\n[Name:{self.name}]\n[ID:{self.id}]\n[AccountID:{self.account_id}]"
        return ret
        
    @property
    def name(self):
        return self.options.get('name')
    
    @property
    def account_id(self):
        return self.options.get('account_id')
    
    def to_user(self):
        from .client import client
        user = client().get_user(self.account_id)
        return user
