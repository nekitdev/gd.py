from .errors import error

class BaseType: # let's assume we don't call repr() of this one
    """This type is not meant to be used as a type, but more as a helper for str() and repr() to other types"""
    def __init__(self):
        self._level = -1
        self._name = type(self).__name__

    def __repr__(self):
        res = f'<gd.types.{type(self).__name__}: level={self.level}, name={repr(self.name)}>'
        return res
    
    def __str__(self):
        res = f'[gd.types.{type(self).__name__}]\n[Level:{self.level}]\n[Name:{self.name}]'
        return res
    
    @property
    def name(self):
        return self._name
    @property
    def level(self):
        return self._level
    
class AbstractPrivacy1Type(BaseType):
    def __init__(self, level):
        super().__init__()
        if type(level) is str:
            try:
                self._level = privacy_1.index(level)
            except ValueError:
                raise error.InvalidArgument()
        if type(level) is int:
            if level > 2 or level < 0:
                raise error.InvalidArgument()
            else:
                self._level = level
    @property
    def level(self):
        return self._level
    @property
    def name(self):
        return privacy_1[self.level]

class AbstractPrivacy2Type(BaseType):
    def __init__(self, level):
        super().__init__()
        if type(level) is str:
            try:
                self._level = privacy_2.index(level)
            except ValueError:
                raise error.InvalidArgument()
        if type(level) is int:
            if level > 1 or level < 0:
                raise error.InvalidArgument()
            else:
                self._level = level

    @property
    def level(self):
        return self._level
    @property
    def name(self):
        return privacy_2[self.level]

class StatusLevelType(BaseType):
    def __init__(self, level):
        super().__init__()
        if type(level) is str:
            try:
                self._level = mod.index(level)
            except ValueError:
                raise error.InvalidArgument()
        if type(level) is int:
            if level > 2 or level < 0:
                raise error.InvalidArgument()
            else:
                self._level = level

    @property
    def level(self):
        return self._level
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