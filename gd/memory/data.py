import struct

from enums import Enum  # type: ignore
from iters import iter

from gd.text_utils import make_repr
from gd.typing import Generic, TypeVar, Union, cast

__all__ = (
    "ByteOrder",
    "Data",
    "get_pointer_type",
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
NULL_BYTE = b"\x00"

T = TypeVar("T")


def read_until_terminator(data: bytes, sentinel: int = 0) -> bytes:
    return cast(bytes, iter(data).take_while(lambda byte: byte != sentinel).collect(bytes))


class ByteOrder(Enum):
    NATIVE = "="
    LITTLE_ENDIAN = "<"
    BIG_ENDIAN = ">"


class Data(Generic[T]):
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
        try:
            unpacked = struct.unpack(self.create_format(order), data)

        except struct.error as error:
            raise ValueError(f"Can not convert data to {self.name}. Error: {error}.")

        if len(unpacked) == 1:
            return cast(T, unpacked[0])

        return cast(T, unpacked)

    def to_bytes(self, value: T, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> bytes:
        try:
            return struct.pack(self.create_format(order), value)

        except struct.error as error:
            raise ValueError(f"Can not convert {self.name} to data. Error: {error}.")

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


class String(Data[str]):
    def __init__(self) -> None:
        super().__init__("string", "")

    def from_bytes(self, data: bytes, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> str:
        return read_until_terminator(data).decode(ENCODING)

    def to_bytes(
        self, value: str, order: Union[str, ByteOrder] = ByteOrder.NATIVE, null: bool = True
    ) -> bytes:
        if null:
            return value.encode(ENCODING) + NULL_BYTE

        return value.encode(ENCODING)


def get_pointer_type(bits: int, signed: bool = False) -> Data[int]:
    if signed:
        choose_from = all_int

    else:
        choose_from = all_uint

    for pointer_type in choose_from:
        if pointer_type.bits == bits:
            return pointer_type

    else:
        raise ValueError("Can not find pointer type that matches given bits.")


boolean: Data[bool] = Data("boolean", "?")

char: Data[bytes] = Data("char", "c")

int8: Data[int] = Data("int8", "b")
uint8: Data[int] = Data("uint8", "B")

int16: Data[int] = Data("int16", "h")
uint16: Data[int] = Data("uint16", "H")

int32: Data[int] = Data("int32", "l")
uint32: Data[int] = Data("uint32", "L")

int64: Data[int] = Data("int64", "q")
uint64: Data[int] = Data("uint64", "Q")

all_int = (int8, int16, int32, int64)
all_uint = (uint8, uint16, uint32, uint64)

float32: Data[float] = Data("float32", "f")
float64: Data[float] = Data("float64", "d")

string: Data[str] = String()
