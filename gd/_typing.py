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
    NoReturn,
    TypeVar,
    Type,
    TYPE_CHECKING,
    no_type_check,
    overload,
)
try:  # pragma: no cover
    from typing import ForwardRef as ref  # type: ignore
except ImportError:  # pragma: no cover
    # python < 3.7
    from typing import _ForwardRef as ref  # type: ignore

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
    'UserStats',
    'User',
    'NEnum',
    'Filters',
    'Parameters',
    'Parser',
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
    'NoReturn',
    'Type',
    'TypeVar',
    'TYPE_CHECKING',
    'no_type_check',
    'overload',
)


def __repr__(forward_ref):
    return str(forward_ref.__forward_arg__)


setattr(ref, '__repr__', __repr__)

AbstractEntity = ref('gd.abstractentity.AbstractEntity')
AbstractUser = ref('gd.abstractuser.AbstractUser')
LevelRecord = ref('gd.abstractuser.LevelRecord')
Client = ref('gd.client.Client')
Color = ref('gd.colors.Color')
Comment = ref('gd.comment.Comment')
FriendRequest = ref('gd.friend_request.FriendRequest')
IconSet = ref('gd.iconset.IconSet')
Level = ref('gd.level.Level')
Gauntlet = ref('gd.level_packs.Gauntlet')
MapPack = ref('gd.level_packs.MapPack')
Message = ref('gd.message.Message')
Song = ref('gd.song.Song')
UserStats = ref('gd.user.UserStats')
User = ref('gd.user.User')
NEnum = ref('gd.utils.enums.NEnum')
Filters = ref('gd.utils.filters.Filters')
Parameters = ref('gd.utils.params.Parameters')
Parser = ref('gd.utils.parser.Parser')
Loop = ref('gd.utils.tasks.Loop')
Editor = ref('gd.api.editor.Editor')
HSV = ref('gd.api.hsv.HSV')
LevelCollection = ref('gd.api.save.LevelCollection')
Struct = ref('gd.api.struct.Struct')
Object = ref('gd.api.struct.Object')
ColorChannel = ref('gd.api.struct.ColorChannel')
ColorCollection = ref('gd.api.struct.ColorCollection')
Header = ref('gd.api.struct.Header')
LevelAPI = ref('gd.api.struct.LevelAPI')
