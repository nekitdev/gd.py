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
    IO,
    Generator,
    Awaitable,
    Coroutine,
    AsyncIterable,
    AsyncIterator,
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

__all__ = (
    "AbstractEntity",
    "AbstractUser",
    "ArtistInfo",
    "Author",
    "Buffer",
    "LevelRecord",
    "Client",
    "Color",
    "Comment",
    "FriendRequest",
    "Guidelines",
    "IconSet",
    "Level",
    "Gauntlet",
    "MapPack",
    "Message",
    "Song",
    "UserStats",
    "User",
    "Filters",
    "Parameters",
    "Parser",
    "Loop",
    "Editor",
    "HSV",
    "LevelCollection",
    "Struct",
    "Object",
    "ColorChannel",
    "ColorCollection",
    "Header",
    "LevelAPI",
    "Any",
    "Callable",
    "Function",
    "Optional",
    "Tuple",
    "Union",
    "Iterable",
    "Iterator",
    "Mapping",
    "Sequence",
    "Dict",
    "List",
    "Set",
    "IO",
    "Generator",
    "Awaitable",
    "Coroutine",
    "AsyncIterable",
    "AsyncIterator",
    "Type",
    "TypeVar",
    "TYPE_CHECKING",
    "no_type_check",
    "overload",
)


def __forward_ref_repr__(self: ref) -> str:
    return str(self.__forward_arg__)


setattr(ref, "__repr__", __forward_ref_repr__)

Function = Callable[..., Any]

AbstractEntity = ref("gd.abstractentity.AbstractEntity")
AbstractUser = ref("gd.abstractuser.AbstractUser")
ArtistInfo = ref("gd.song.ArtistInfo")
Author = ref("gd.song.Author")
Buffer = ref("gd.memory.interface.Buffer")
LevelRecord = ref("gd.abstractuser.LevelRecord")
Client = ref("gd.client.Client")
Color = ref("gd.colors.Color")
Comment = ref("gd.comment.Comment")
FriendRequest = ref("gd.friend_request.FriendRequest")
Guidelines = ref("gd.api.guidelines.Guidelines")
HTMLElement = ref("lxml.html.HtmlElement")
XMLElement = ref("xml.etree.ElementTree.Element")
IconSet = ref("gd.iconset.IconSet")
Level = ref("gd.level.Level")
Gauntlet = ref("gd.level_packs.Gauntlet")
MapPack = ref("gd.level_packs.MapPack")
Message = ref("gd.message.Message")
Song = ref("gd.song.Song")
UserStats = ref("gd.user.UserStats")
User = ref("gd.user.User")
Filters = ref("gd.utils.filters.Filters")
Parameters = ref("gd.utils.params.Parameters")
Parser = ref("gd.utils.parser.Parser")
Loop = ref("gd.utils.tasks.Loop")
Editor = ref("gd.api.editor.Editor")
HSV = ref("gd.api.hsv.HSV")
LevelCollection = ref("gd.api.save.LevelCollection")
Struct = ref("gd.api.struct.Struct")
Object = ref("gd.api.struct.Object")
ColorChannel = ref("gd.api.struct.ColorChannel")
ColorCollection = ref("gd.api.struct.ColorCollection")
Header = ref("gd.api.struct.Header")
LevelAPI = ref("gd.api.struct.LevelAPI")
