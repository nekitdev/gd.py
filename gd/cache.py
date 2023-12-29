from __future__ import annotations

from typing import TYPE_CHECKING, Dict, TypeVar

from attrs import define, field

if TYPE_CHECKING:
    from gd.artist import Artist
    from gd.comments import LevelComment, UserComment
    from gd.friend_requests import FriendRequest
    from gd.level_packs import Gauntlet, MapPack
    from gd.levels import Level
    from gd.messages import Message
    from gd.songs import Song
    from gd.users import User

__all__ = ("CacheSettings", "Cache", "CachePart")

DEFAULT_SIZE = 0


@define()
class CacheSettings:
    artist_size: int = DEFAULT_SIZE
    user_comment_size: int = DEFAULT_SIZE
    level_comment_size: int = DEFAULT_SIZE
    friend_request_size: int = DEFAULT_SIZE
    gauntlet_size: int = DEFAULT_SIZE
    map_pack_size: int = DEFAULT_SIZE
    level_size: int = DEFAULT_SIZE
    message_size: int = DEFAULT_SIZE
    song_size: int = DEFAULT_SIZE
    user_size: int = DEFAULT_SIZE


T = TypeVar("T")

CachePart = Dict[int, T]


@define()
class Cache:
    settings: CacheSettings = field(factory=CacheSettings)

    artists: CachePart[Artist] = field(factory=dict)
    user_comments: CachePart[UserComment] = field(factory=dict)
    level_comments: CachePart[LevelComment] = field(factory=dict)
    friend_requests: CachePart[FriendRequest] = field(factory=dict)
    gauntlets: CachePart[Gauntlet] = field(factory=dict)
    map_packs: CachePart[MapPack] = field(factory=dict)
    levels: CachePart[Level] = field(factory=dict)
    messages: CachePart[Message] = field(factory=dict)
    songs: CachePart[Song] = field(factory=dict)
    users: CachePart[User] = field(factory=dict)
