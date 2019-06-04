from .errors import error

class AbstractPrivacy1Type:
    def __init__(self, level):
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

class AbstractPrivacy2Type:
    def __init__(self, level):
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

class StatusLevelType:
    def __init__(self, level):
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