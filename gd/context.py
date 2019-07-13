from .utils.wrap_tools import Abstract

class Context(Abstract):
    def __init__(self):
        self.id = 0
        self.user = None
        self.password = None
        self.__to_repr__ = ['id', 'user', 'password']

    def upd(self, attr, value):
        if not hasattr(self, attr):
            raise AttributeError(f"Method 'upd(self, attr, value)' of '{self.__class__.__name__}' expected 'attr' to be already defined.")
        setattr(self, attr, value)

ctx = context = Context()

# TO_DO: add something else if needed.
