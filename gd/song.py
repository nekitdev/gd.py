from __future__ import annotations

from io import BytesIO
from typing import BinaryIO, Optional, Type, TypeVar

from attrs import define
from iters import iter
from yarl import URL

from gd.artist import Artist
from gd.binary_utils import UTF_8, Reader, Writer
from gd.constants import (
    DEFAULT_FROM_NEWGROUNDS,
    DEFAULT_ID,
    DEFAULT_RETURN_DEFAULT,
    DEFAULT_SERVER_STYLE,
    DEFAULT_SIZE,
    DEFAULT_WITH_BAR,
    EMPTY,
    UNKNOWN,
)
from gd.entity import Entity
from gd.enums import ByteOrder
from gd.errors import MissingAccess

# from gd.http import NEWGROUNDS_SONG_LISTEN
from gd.models import SongModel
from gd.official_songs import (
    OFFICIAL_CLIENT_SONGS,
    OFFICIAL_SERVER_SONGS,
    OfficialSong,
    create_default_offical_song,
)
from gd.typing import IntoPath, Predicate

__all__ = ("Song",)


def by_id(id: int) -> Predicate[OfficialSong]:
    def predicate(offical_song: OfficialSong) -> bool:
        return offical_song.id == id

    return predicate


def by_name(name: str) -> Predicate[OfficialSong]:
    def predicate(offical_song: OfficialSong) -> bool:
        return offical_song.name == name

    return predicate


S = TypeVar("S", bound="Song")

EXPECTED_QUERY = "expected either `id` or `name` query"
CAN_NOT_FIND_SONG = "can not find official song by given query"
CAN_NOT_DOWNLOAD = "can not download an official song"
CAN_NOT_FIND_URL = "can not find download URL"

WRITE_BINARY = "wb"

DEFAULT_CUSTOM = True


@define()
class Song(Entity):
    """Represents Geometry Dash and Newgrounds songs."""

    name: str
    artist: Artist
    size: float = DEFAULT_SIZE

    custom: bool = DEFAULT_CUSTOM

    download_url: Optional[URL] = None

    @classmethod
    def from_binary(
        cls: Type[S], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, encoding: str = UTF_8
    ) -> S:
        reader = Reader(binary)

        id = reader.read_u32(order)

        name_length = reader.read_u8(order)

        name = reader.read(name_length).decode(encoding)

        artist = Artist.from_binary(binary, order, encoding)

        size = reader.read_f32(order)

        custom = bool(reader.read_u8(order))

        download_url_length = reader.read_u16(order)

        string = reader.read(download_url_length).decode(encoding)

        if not string:
            download_url = None

        else:
            download_url = URL(string)

        return cls(
            id=id, name=name, artist=artist, size=size, custom=custom, download_url=download_url
        )

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, encoding: str = UTF_8
    ) -> None:
        writer = Writer(binary)

        writer.write_u32(self.id, order)

        data = self.name.encode(encoding)

        writer.write_u8(len(data), order)

        writer.write(data)

        self.artist.to_binary(binary, order, encoding)

        writer.write_f32(self.size, order)

        writer.write_u8(int(self.custom), order)

        download_url = self.download_url

        if download_url is None:
            string = EMPTY

        else:
            string = str(download_url)

        data = string.encode(encoding)

        writer.write_u16(len(data), order)

        writer.write(data)

    @classmethod
    def default(cls: Type[S]) -> S:
        return cls(DEFAULT_ID, UNKNOWN, Artist.default())

    @classmethod
    def from_model(cls: Type[S], model: SongModel) -> S:
        return cls(
            id=model.id,
            name=model.name,
            artist=Artist(model.artist_name),
            size=model.size,
            download_url=model.download_url,
        )

    def __str__(self) -> str:
        return self.name

    @property
    def link(self) -> str:
        if self.is_custom():
            return NEWGROUNDS_SONG_LISTEN.format(self.id)

        raise

    def is_custom(self) -> bool:
        return self.custom

    @classmethod
    def official(
        cls: Type[S],
        id: Optional[int] = None,
        name: Optional[str] = None,
        server_style: bool = DEFAULT_SERVER_STYLE,
        return_default: bool = DEFAULT_RETURN_DEFAULT,
    ) -> S:
        official_songs = OFFICIAL_SERVER_SONGS if server_style else OFFICIAL_CLIENT_SONGS

        if id is None:
            if name is None:
                raise LookupError(EXPECTED_QUERY)

            official_song = iter(official_songs).find(by_name(name))

        else:
            official_song = iter(official_songs).find(by_id(id))

        if official_song is None:
            if return_default:
                official_song = (
                    create_default_offical_song() if id is None else create_default_offical_song(id)
                )

            else:
                raise LookupError(CAN_NOT_FIND_SONG)

        return cls(
            id=official_song.id,
            name=official_song.name,
            size=DEFAULT_SIZE,
            artist=official_song.artist,
            custom=False,
        )

    async def update(self, from_newgrounds: bool = DEFAULT_FROM_NEWGROUNDS) -> None:
        if from_newgrounds:
            new = await self.client.get_newgrounds_song(self.id)

        else:
            new = await self.client.get_song(self.id)

        self.update_from(new)

    async def download(self, file: BinaryIO, with_bar: bool = DEFAULT_WITH_BAR) -> None:
        if self.is_custom():
            download_url = self.download_url

            if download_url is None:
                await self.update(from_newgrounds=True)

            download_url = self.download_url

            if download_url is None:
                raise MissingAccess(CAN_NOT_FIND_URL)

            return await self.client.http.download(download_url, file=file, with_bar=with_bar)

        else:
            raise MissingAccess(CAN_NOT_DOWNLOAD)

    async def download_bytes(self, with_bar: bool = DEFAULT_WITH_BAR) -> bytes:
        file = BytesIO()

        await self.download(file, with_bar=with_bar)

        file.seek(0)

        return file.read()

    async def download_to(self, path: IntoPath, with_bar: bool = DEFAULT_WITH_BAR) -> None:
        with open(path, WRITE_BINARY) as file:
            await self.download(file, with_bar=with_bar)
