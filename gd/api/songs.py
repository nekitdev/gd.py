from typing import Any, Optional, Type, TypeVar

from attrs import define
from typing_aliases import StringDict, StringMapping
from yarl import URL

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import (
    DEFAULT_CUSTOM,
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    DEFAULT_ID,
    DEFAULT_PRIORITY,
    DEFAULT_ROUNDING,
    DEFAULT_SIZE,
    EMPTY,
)
from gd.converter import dump_url
from gd.enums import ByteOrder, InternalType

__all__ = ("SongReferenceAPI", "ArtistAPI", "SongAPI")

INTERNAL_TYPE = "kCEK"

ID = "1"
NAME = "2"
ARTIST_ID = "3"
ARTIST_NAME = "4"
SIZE = "5"
# not using YouTube-related things here intentionally ~ nekit
PRIORITY = "9"
DOWNLOAD_URL = "10"

CUSTOM_BIT = 0b10000000_00000000_00000000_00000000
ID_MASK = 0b01111111_11111111_11111111_11111111

R = TypeVar("R", bound="SongReferenceAPI")


@define()
class SongReferenceAPI(Binary):
    id: int
    custom: bool

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.to_value()

    def is_custom(self) -> bool:
        return self.custom

    @classmethod
    def default(cls: Type[R], id: int = DEFAULT_ID, custom: bool = DEFAULT_CUSTOM) -> R:
        return cls(id=id, custom=custom)

    @classmethod
    def from_value(cls: Type[R], value: int) -> R:
        custom_bit = CUSTOM_BIT

        custom = value & custom_bit == custom_bit

        id = value & ID_MASK

        return cls(id=id, custom=custom)

    def to_value(self) -> int:
        value = self.id

        if self.is_custom():
            value |= CUSTOM_BIT

        return value

    @classmethod
    def from_binary(
        cls: Type[R],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> R:
        reader = Reader(binary, order)

        value = reader.read_u32()

        return cls.from_value(value)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        writer = Writer(binary, order)

        value = self.to_value()

        writer.write_u32(value)


A = TypeVar("A", bound="ArtistAPI")


@define()
class ArtistAPI(Binary):
    id: int
    name: str

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @classmethod
    def default(cls: Type[A], id: int = DEFAULT_ID) -> A:
        return cls(id=id, name=EMPTY)

    @classmethod
    def from_binary(
        cls: Type[A],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> A:
        reader = Reader(binary, order)

        id = reader.read_u32()

        name_length = reader.read_u8()

        name = reader.read(name_length).decode(encoding, errors)

        return cls(id=id, name=name)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u32(self.id)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data))

        writer.write(data)


S = TypeVar("S", bound="SongAPI")


@define()
class SongAPI(Binary):
    id: int
    name: str
    artist: ArtistAPI
    size: float = DEFAULT_SIZE
    priority: int = DEFAULT_PRIORITY
    download_url: Optional[URL] = None

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @classmethod
    def default(cls: Type[S], id: int = DEFAULT_ID, artist_id: int = DEFAULT_ID) -> S:
        return cls(id=id, name=EMPTY, artist=ArtistAPI.default(artist_id))

    @classmethod
    def from_robtop_data(cls: Type[S], data: StringMapping[Any]) -> S:  # type: ignore
        id = data.get(ID, DEFAULT_ID)
        name = data.get(NAME, EMPTY)
        artist_id = data.get(ARTIST_ID, DEFAULT_ID)
        artist_name = data.get(ARTIST_NAME, EMPTY)
        size = data.get(SIZE, DEFAULT_SIZE)
        priority = data.get(PRIORITY, DEFAULT_PRIORITY)

        download_url_string = data.get(DOWNLOAD_URL, EMPTY)

        download_url = URL(download_url_string) if download_url_string else None

        return cls(
            id=id,
            name=name,
            artist=ArtistAPI(id=artist_id, name=artist_name),
            size=size,
            priority=priority,
            download_url=download_url,
        )

    def to_robtop_data(self) -> StringDict[Any]:
        artist = self.artist

        download_url = self.download_url

        data = {
            INTERNAL_TYPE: InternalType.SONG.value,
            ID: self.id,
            NAME: self.name,
            ARTIST_ID: artist.id,
            ARTIST_NAME: artist.name,
            SIZE: self.size,
            PRIORITY: self.priority,
            DOWNLOAD_URL: EMPTY if download_url is None else str(download_url),
        }

        return data

    @classmethod
    def from_binary(
        cls: Type[S],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> S:
        rounding = DEFAULT_ROUNDING

        reader = Reader(binary, order)

        id = reader.read_u32()

        name_length = reader.read_u8()

        name = reader.read(name_length).decode(encoding, errors)

        artist = ArtistAPI.from_binary(binary, order, version, encoding, errors)

        size = round(reader.read_f32(), rounding)

        priority = reader.read_u32()

        download_url_length = reader.read_u16()

        if download_url_length:
            download_url_string = reader.read(download_url_length).decode(encoding, errors)

            download_url = URL(download_url_string)

        else:
            download_url = None

        return cls(
            id=id,
            name=name,
            artist=artist,
            size=size,
            priority=priority,
            download_url=download_url,
        )

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u32(self.id)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data))

        writer.write(data)

        self.artist.to_binary(binary, order, version, encoding, errors)

        writer.write_f32(self.size)

        writer.write_u32(self.priority)

        download_url = self.download_url

        if download_url is None:
            writer.write_u16(0)

        else:
            data = dump_url(download_url).encode(encoding, errors)

            writer.write_u16(len(data))

            writer.write(data)
