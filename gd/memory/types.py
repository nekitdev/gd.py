import struct

from enums import Enum  # type: ignore

from gd.text_utils import make_repr
from gd.typing import Generic, TypeVar, Union, cast

__all__ = (
    "ByteOrder",
    "Type",
    "boolean",
    "char",
    "int8",
    "uint8",
    "int16",
    "uint16",
    "int32",
    "uint32",
    "int64",
    "uint64",
    "float32",
    "float64",
    "string",
)

ENCODING = "utf-8"
NULL_BYTE = br"\0"

T = TypeVar("T")


class ByteOrder(Enum):
    NATIVE = "="
    LITTLE_ENDIAN = "<"
    BIG_ENDIAN = ">"


class Type(Generic[T]):
    def __init__(self, name: str, format: str) -> None:
        self._name = name
        self._format = format
        self._size = struct.calcsize(format)

        cls = self.__class__

        if not hasattr(cls, name):
            setattr(cls, name, self)

    def __repr__(self) -> str:
        info = {"name": repr(self.name), "size": self.size}
        return make_repr(self, info)

    def __str__(self) -> str:
        return self.name

    def create_format(self, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> str:
        return ByteOrder.from_value(order).value + self.format

    def from_bytes(self, data: bytes, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> T:
        unpacked = struct.unpack(self.create_format(order), data)

        if len(unpacked) == 1:
            return cast(T, unpacked[0])

        return cast(T, unpacked)

    def to_bytes(self, value: T, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> bytes:
        return struct.pack(self.create_format(order), value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def format(self) -> str:
        return self._format

    @property
    def size(self) -> int:
        return self._size

    @property
    def bytes(self) -> int:
        return self._size

    @property
    def bits(self):
        return self._size << 3


class String(Type[str]):
    def __init__(self) -> None:
        super().__init__("string", "")

    def from_bytes(self, data: bytes, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> str:
        return data.decode(ENCODING)

    def to_bytes(self, value: str, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> bytes:
        return value.encode(ENCODING)


boolean: Type[bool] = Type("boolean", "?")

char: Type[bytes] = Type("char", "c")

int8: Type[int] = Type("int8", "b")
uint8: Type[int] = Type("uint8", "B")

int16: Type[int] = Type("int16", "h")
uint16: Type[int] = Type("uint16", "H")

int32: Type[int] = Type("int32", "l")
uint32: Type[int] = Type("uint32", "L")

int64: Type[int] = Type("int64", "q")
uint64: Type[int] = Type("uint64", "Q")

float32: Type[float] = Type("float32", "f")
float64: Type[float] = Type("float64", "d")

string: Type[str] = String()
