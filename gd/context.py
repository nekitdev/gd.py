class Context:
    def __init__(self):
        self.id = 0
        self.user = None
        self.password = None

    def upd(self, attr, value):
        if not hasattr(self, attr):
            raise AttributeError(f"Method 'upd(self, attr, value)' of '{self.__class__.__name__}' expected 'attr' to be already defined.")
        setattr(self, attr, value)

ctx = context = Context()

# TO_DO: add 'Abstract' class which should contain '__repr__' and other methods and attributes.
