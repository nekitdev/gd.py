from .wrap_tools import _make_repr

class BaseType:
    """This type is not meant to be used as a type, but more as a helper for str() and repr() to other types"""
    def __init__(self):
        self._level = -1
        self._name = None

    def __repr__(self):
        info = {
            'level': self.level,
            'name': repr(self.name)
        }
        return _make_repr(self, info)
    
    @property
    def name(self):
        return self._name

    @property
    def level(self):
        return self._level

privacy_1 = (
    'Opened to all',
    'Opened to friends only',
    'Closed'
)

privacy_2 = (
    'Opened',
    'Closed'
)

mod = (
    'User',
    'Moderator',
    'Elder Moderator'
)


class AbstractPrivacy1Type(BaseType):
    def __init__(self, level):
        super().__init__()
        if isinstance(level, str):
            try:
                self._level = privacy_1.index(level)
            except ValueError:
                raise error.InvalidArgument()
        if isinstance(level, int):
            self._level = level

    @property
    def name(self):
        return privacy_1[self.level]


class AbstractPrivacy2Type(BaseType):
    def __init__(self, level):
        super().__init__()
        if isinstance(level, str):
            try:
                self._level = privacy_2.index(level)
            except ValueError:
                raise error.InvalidArgument()
        if isinstance(level, int):
            self._level = level

    @property
    def name(self):
        return privacy_2[self.level]


class StatusLevelType(BaseType):
    def __init__(self, level):
        super().__init__()
        if isinstance(level, str):
            try:
                self._level = mod.index(level)
            except ValueError:
                raise error.InvalidArgument()
        if isinstance(level, int):
            self._level = level

    @property
    def name(self):
        return mod[self.level]


class MessagePrivacyType(AbstractPrivacy1Type):
    def __init__(self, level):
        super().__init__(level)


class FriendRequestPrivacyType(AbstractPrivacy2Type):
    def __init__(self, level):
        super().__init__(level)


class CommentPrivacyType(AbstractPrivacy1Type):
    def __init__(self, level):
        super().__init__(level)
