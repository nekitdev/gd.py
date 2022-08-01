from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Iterable, Type, TypeVar

from attrs import field, frozen
from yarl import URL

from gd.await_iters import wrap_await_iter
from gd.constants import DEFAULT_PAGE, DEFAULT_PAGES, UNKNOWN
from gd.entity import Entity
from gd.string_utils import case_fold, clear_whitespace

if TYPE_CHECKING:
    from gd.song import Song

__all__ = ("Artist",)

A = TypeVar("A", bound="Artist")

ARTIST = "https://{}.newgrounds.com/"


@frozen()
class Artist(Entity):
    """Represents artists on *Newgrounds*."""

    name: str = field()

    url: URL = field(converter=URL)

    id: int = field()

    @id.default
    def default_id(self) -> int:
        return hash(self.name) ^ hash(self.url)

    @url.default
    def default_url(self) -> URL:
        return URL(ARTIST.format(self.id_name))

    @property
    def id_name(self) -> str:
        return clear_whitespace(case_fold(self.name))

    @classmethod
    def default(cls: Type[A]) -> A:
        return cls(UNKNOWN)

    def __str__(self) -> str:
        return self.name

    @wrap_await_iter
    def get_songs_on_page(self, page: int = DEFAULT_PAGE) -> AsyncIterator[Song]:
        return self.client.get_newgrounds_artist_songs_on_page(self, page=page)

    @wrap_await_iter
    def get_songs(self, pages: Iterable[int] = DEFAULT_PAGES) -> AsyncIterator[Song]:
        return self.client.get_newgrounds_artist_songs(self, pages=pages)
