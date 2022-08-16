from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, BinaryIO, Iterable, Type, TypeVar

from attrs import field, frozen
from iters.async_iters import wrap_async_iter
from yarl import URL

from gd.binary import VERSION
from gd.binary_utils import UTF_8, Reader, Writer
from gd.constants import DEFAULT_PAGE, DEFAULT_PAGES, UNKNOWN
from gd.entity import Entity
from gd.enums import ByteOrder
from gd.string_utils import case_fold, clear_whitespace


if TYPE_CHECKING:
    from gd.song import Song

__all__ = ("Artist",)

A = TypeVar("A", bound="Artist")

ARTIST = "https://{}.newgrounds.com/"


@frozen(hash=True)
class Artist(Entity):
    """Represents artists on *Newgrounds*."""

    name: str = field()

    url: URL = field(converter=URL)

    id: int = field(repr=False)

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
        return cls(name=UNKNOWN)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_binary(
        cls: Type[A],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = UTF_8,
    ) -> A:
        reader = Reader(binary)

        length = reader.read_u8(order)

        data = reader.read(length)

        name = data.decode(encoding)

        return cls(name=name)

    def to_binary(
        self,
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = UTF_8,
    ) -> None:
        writer = Writer(binary)

        data = self.name.encode(encoding)

        writer.write_u8(len(data))

        writer.write(data)

    @wrap_async_iter
    def get_songs_on_page(self, page: int = DEFAULT_PAGE) -> AsyncIterator[Song]:
        return self.client.get_newgrounds_artist_songs_on_page(self, page=page)

    @wrap_async_iter
    def get_songs(self, pages: Iterable[int] = DEFAULT_PAGES) -> AsyncIterator[Song]:
        return self.client.get_newgrounds_artist_songs(self, pages=pages)
