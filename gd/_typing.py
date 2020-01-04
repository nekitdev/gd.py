from typing import (
    Any,
    Callable,
    Optional,
    Tuple,
    Union,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
    Dict,
    List,
    Set,
    Generator,
    Awaitable,
    Coroutine,
    AsyncIterable,
    AsyncIterator,
    TypeVar,
    Type,
    TYPE_CHECKING,
    no_type_check,
)
from enum import Enum

__all__ = (
    'AbstractEntity',
    'AbstractUser',
    'LevelRecord',
    'Client',
    'Color',
    'Comment',
    'FriendRequest',
    'IconSet',
    'Level',
    'Gauntlet',
    'MapPack',
    'Message',
    'Song',
    'UnregisteredUser',
    'UserStats',
    'User',
    'Filters',
    'Parameters',
    'Loop',
    'Enum',
    'Editor',
    'HSV',
    'LevelCollection',
    'Struct',
    'Object',
    'ColorChannel',
    'ColorCollection',
    'Header',
    'LevelAPI',
    'Any',
    'Callable',
    'Optional',
    'Tuple',
    'Union',
    'Iterable',
    'Iterator',
    'Mapping',
    'Sequence',
    'Dict',
    'List',
    'Set',
    'Generator',
    'Awaitable',
    'Coroutine',
    'AsyncIterable',
    'AsyncIterator',
    'Type',
    'TYPE_CHECKING',
    'no_type_check',
)


def _modify_typevar():
    def __repr__(self):
        if self.__covariant__:
            prefix = '+'
        elif self.__contravariant__:
            prefix = '-'
        else:
            prefix = str()
        return prefix + self.__name__

    TypeVar.__repr__ = __repr__


if TYPE_CHECKING:
    from .abstractentity import AbstractEntity
    from .abstractuser import AbstractUser, LevelRecord
    from .client import Client
    from .colors import Color
    from .comment import Comment
    from .friend_request import FriendRequest
    from .iconset import IconSet
    from .level import Level
    from .level_packs import Gauntlet, MapPack
    from .message import Message
    from .song import Song
    from .unreguser import UnregisteredUser
    from .user import UserStats, User
    from .utils.filters import Filters
    from .utils.params import Parameters
    from .utils.tasks import Loop
    from .api.editor import Editor
    from .api.hsv import HSV
    from .api.save import LevelCollection
    from .api.struct import Struct, Object, ColorChannel, ColorCollection, Header, LevelAPI

else:
    # TypeVar('SomeString') allows any type,
    # but nekit does not like string annotations.
    AbstractEntity = TypeVar('AbstractEntity')
    AbstractUser = TypeVar('AbstractUser')
    LevelRecord = TypeVar('LevelRecord')
    Client = TypeVar('Client')
    Color = TypeVar('Color')
    Comment = TypeVar('Comment')
    FriendRequest = TypeVar('FriendRequest')
    IconSet = TypeVar('IconSet')
    Level = TypeVar('Level')
    Gauntlet = TypeVar('Gauntlet')
    MapPack = TypeVar('MapPack')
    Message = TypeVar('Message')
    Song = TypeVar('Song')
    UnregisteredUser = TypeVar('UnregisteredUser')
    UserStats = TypeVar('UserStats')
    User = TypeVar('User')
    Filters = TypeVar('Filters')
    Parameters = TypeVar('Parameters')
    Loop = TypeVar('Loop')
    Editor = TypeVar('Editor')
    HSV = TypeVar('HSV')
    LevelCollection = TypeVar('LevelCollection')
    Struct = TypeVar('Struct')
    Object = TypeVar('Object')
    ColorChannel = TypeVar('ColorChannel')
    ColorCollection = TypeVar('ColorCollection')
    Header = TypeVar('Header')
    LevelAPI = TypeVar('LevelAPI')
    _modify_typevar()
