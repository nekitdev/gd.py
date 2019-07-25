from .wrap_tools import _make_repr
from .crypto.coders import Coder

class Context:
    def __init__(self):
        self.account_id = 0
        self.id = 0
        self.name = None
        self.password = None
        self.encodedpass = None

    def __repr__(self):
        info = {
            'account_id': self.account_id,
            'id': self.id,
            'name': self.name,
            'password': self.password
        }
        return _make_repr(self, info)

    def upd(self, attr, value):
        # raise error if not hasattr(self, attr)
        getattr(self, attr, value)
        # update
        setattr(self, attr, value)
        # update encodedpass if password was updated
        if attr == 'password':
            self.encodedpass = Coder().encode0(type='accountpass', string=self.password)

    def is_logged(self):
        return (self.name is not None) and (self.password is not None)

ctx = context = Context()
