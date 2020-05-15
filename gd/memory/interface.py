import ctypes
import itertools
import struct
import sys

try:
    from .win import (
        get_base_address,
        get_handle,
        get_pid_from_name,
        read_process_memory,
        write_process_memory,
    )
except Exception:  # noqa
    pass

from .enums import LevelType, Scene
from ..api.enums import SpeedConstant
from ..errors import FailedConversion
from ..typing import Any, Buffer, Sequence, Tuple, Union
from ..utils.converter import Converter
from ..utils.enums import LevelDifficulty, DemonDifficulty
from ..utils.text_tools import make_repr

__all__ = ("Memory", "MemoryType", "WindowsMemory", "MacOSMemory", "Buffer", "get_memory")

ORDER = {"big": ">", "little": "<"}
DEFAULT_ORDER = "little"
NULL_BYTE = b"\x00"


def read_until_terminator(data: bytes, terminator: int = 0) -> bytes:
    return bytes(itertools.takewhile(lambda char: char != terminator, data))


class MemoryType:
    """Pure type for Memory objects to inherit from."""

    pass


class Buffer:
    """Type that allows to unwrap bytes that were read into different Python types."""

    def __init__(self, data: bytes, order: str = DEFAULT_ORDER) -> None:
        self.data = data
        self.order = order

    def __str__(self) -> str:
        return self.to_format()

    def __repr__(self) -> str:
        info = {"data": repr(self.to_format())}
        return make_repr(self, info)

    def with_order(self, order: str) -> Buffer:
        self.order = order
        return self

    @classmethod
    def from_int(cls, integer: int, size: int = 4, order: str = DEFAULT_ORDER) -> Buffer:
        data = integer.to_bytes(size, order)
        return cls(data, order)

    def as_int(self) -> int:
        return int.from_bytes(self.data, self.order)

    def as_bool(self) -> bool:
        return self.as_int() != 0

    @classmethod
    def from_float(cls, number: float, order: str = DEFAULT_ORDER) -> Buffer:
        mode = ORDER[order] + "f"

        try:
            data = struct.pack(mode, number)
        except Exception as error:
            raise ValueError(f"Could not convert to float. Error: {error}.") from None
        else:
            return cls(data, order)

    def as_float(self) -> float:
        mode = ORDER[self.order] + "f"

        try:
            return struct.unpack(mode, self.data)[0]
        except Exception as error:
            raise ValueError(f"Could not convert from float. Error: {error}.") from None

    @classmethod
    def from_double(cls, number: float, order: str = DEFAULT_ORDER) -> Buffer:
        mode = ORDER[order] + "d"

        try:
            data = struct.pack(mode, number)
        except Exception as error:
            raise ValueError(f"Could not convert from double. Error: {error}.") from None
        else:
            return cls(data, order)

    def as_double(self) -> float:
        mode = ORDER[self.order] + "d"

        try:
            return struct.unpack(mode, self.data)[0]
        except Exception as error:
            raise ValueError(f"Could not convert to double. Error: {error}.") from None

    @classmethod
    def from_str(cls, string: str, terminate: bool = True, order: str = DEFAULT_ORDER) -> Buffer:
        data = string.encode()

        if terminate:
            data += NULL_BYTE

        return cls(data, order)

    def as_str(self, encoding: str = "utf-8", errors: str = "strict") -> str:
        return read_until_terminator(self.data).decode(encoding, errors)

    @classmethod
    def from_format(cls, format_str: str) -> Buffer:
        # format should be something like "6A 14 8B CB FF"
        array = [int(byte, 16) for byte in format_str.split()]
        return cls.from_byte_array(array)

    def to_format(self) -> str:
        return " ".join(format(byte, "02X") for byte in self.data)

    @classmethod
    def from_byte_array(cls, array: Sequence[int]) -> Buffer:
        return cls(bytes(array))

    def into_buffer(self) -> Any:
        return ctypes.create_string_buffer(self.data)


class Memory(MemoryType):
    """Simple wrapper with platform check."""

    def __new__(cls, *args, **kwargs) -> MemoryType:
        if sys.platform == "win32":
            return WindowsMemory(*args, **kwargs)
        # elif sys.platform == "darwin":
        # return MacOSMemory(*args, **kwargs)
        else:
            raise OSError("Only Windows is currently supported.")


class MacOSMemory(MemoryType):
    pass


class WindowsMemory(MemoryType):
    # [GeometryDash.exe + 0x3222D0] + 0x168 -> Editor object
    # [[[GeometryDash.exe + 0x3222D0] + 0x164] + 0x22C] + 0x114 -> Level object
    PTR_LEN = 4
    STR_LEN = 16

    loaded = False
    process_handle = 0
    process_id = 0
    process_name = "undefined"
    base_address = 0

    def __init__(self, process_name: str, load: bool = False) -> None:
        self.process_name = process_name

        if load:
            self.load()

    def __repr__(self) -> str:
        info = {
            "name": repr(self.process_name),
            "pid": self.process_id,
            "base_addr": format(self.base_address, "X"),
            "handle": format(self.process_handle, "X"),
            "loaded": self.loaded,
        }
        return make_repr(self, info)

    def read_at(self, n: int = 0, address: int = 0) -> Buffer:
        buffer = ctypes.create_string_buffer(n)

        read_process_memory(
            self.process_handle, ctypes.c_void_p(address), ctypes.byref(buffer), n, None
        )
        return Buffer(buffer.raw)

    def write_at(self, buffer: Buffer, address: int = 0) -> None:
        data = buffer.into_buffer()
        write_process_memory(
            self.process_handle, ctypes.c_void_p(address), ctypes.byref(data), len(data), None
        )

    def read_bytes(self, n: int = 0, address: int = 0, *offsets) -> Buffer:
        address = self.base_address + address

        for offset in offsets:
            address = self.read_at(self.PTR_LEN, address).as_int() + offset

        return self.read_at(n, address)

    def write_bytes(self, buffer: Buffer, address: int = 0, *offsets) -> None:
        address = self.base_address + address

        for offset in offsets:
            address = self.read_at(self.PTR_LEN, address).as_int() + offset

        self.write_at(buffer, address)

    def read_string(self, base: int, offset: int) -> str:
        address, size_address = base + offset, base + offset + 0x10

        size = self.read_at(4, size_address).as_int()

        if size < self.STR_LEN:
            return self.read_at(size, address).as_str()

        else:
            address = self.read_at(self.PTR_LEN, address).as_int()

            return self.read_at(size, address).as_str()

    def load(self) -> None:
        self.process_id = get_pid_from_name(self.process_name)
        self.process_handle = get_handle(self.process_id)
        self.base_address = get_base_address(self.process_id, self.process_name)
        self.loaded = True

    def is_loaded(self) -> bool:
        return self.loaded

    def reload(self) -> None:
        self.load()

    def get_scene_value(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x1DC).as_int()

    def get_scene(self) -> Scene:
        try:
            return Scene.from_value(self.get_scene_value())
        except FailedConversion:
            return Scene.UNKNOWN

    def get_resolution_value(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x2E0).as_int()

    def get_resolution(self) -> Tuple[int, int]:
        return number_to_resolution.get(self.get_resolution_value(), (0, 0))

    def get_level_id_fast(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x2A0).as_int()

    def is_in_editor(self) -> bool:
        return self.read_bytes(4, 0x3222D0, 0x168).as_bool()

    def is_dead(self) -> bool:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x39C).as_bool()

    def get_object_count(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x168, 0x3A0).as_int()

    def get_percent(self) -> float:
        return self.read_bytes(8, 0x3222D0, 0x164, 0x450).as_double()

    def get_x_pos(self) -> float:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x224, 0x67C).as_float()

    def set_x_pos(self, pos: float) -> None:
        self.write_bytes(Buffer.from_float(pos), 0x3222D0, 0x164, 0x224, 0x67C)

    def get_y_pos(self) -> float:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x224, 0x680).as_float()

    def set_y_pos(self, pos: float) -> None:
        self.write_bytes(Buffer.from_float(pos), 0x3222D0, 0x164, 0x224, 0x680)

    def get_speed_value(self) -> float:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x224, 0x648).as_float()

    def set_speed_value(self, value: float) -> None:
        self.write_bytes(Buffer.from_float(value), 0x3222D0, 0x164, 0x224, 0x648)

    def get_speed(self) -> SpeedConstant:
        try:
            return SpeedConstant.from_value(round(self.get_speed_value(), 1))
        except FailedConversion:
            return SpeedConstant.NULL

    def get_level_id(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114, 0xF8).as_int()

    def get_level_name(self) -> str:
        base = self.read_bytes(self.PTR_LEN, 0x3222D0, 0x164, 0x22C, 0x114).as_int()
        return self.read_string(base, 0xFC)

    def get_level_creator(self) -> str:
        base = self.read_bytes(self.PTR_LEN, 0x3222D0, 0x164, 0x22C, 0x114).as_int()
        return self.read_string(base, 0x144)

    def get_level_stars(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114, 0x2AC).as_int()

    def is_level_demon(self) -> bool:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114, 0x29C).as_bool()

    def is_level_auto(self) -> bool:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114, 0x2B0).as_bool()

    def get_level_diff_value(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114, 0x1E4).as_int()

    def get_level_demon_diff_value(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114, 0x2A0).as_int()

    def get_level_difficulty(self) -> Union[LevelDifficulty, DemonDifficulty]:
        address = self.read_bytes(self.PTR_LEN, 0x3222D0, 0x164, 0x22C, 0x114).as_int()

        is_demon, is_auto, diff, demon_diff = (  # optimized
            self.read_at(4, address + 0x29C).as_bool(),
            self.read_at(4, address + 0x2B0).as_bool(),
            self.read_at(4, address + 0x1E4).as_int(),
            self.read_at(4, address + 0x2A0).as_int(),
        )

        return Converter.convert_level_difficulty(
            diff=diff, demon_diff=demon_diff, is_demon=is_demon, is_auto=is_auto
        )

    def get_attempts(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114, 0x218).as_int()

    def get_jumps(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114, 0x224).as_int()

    def get_normal_percent(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114, 0x248).as_int()

    def get_practice_percent(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114, 0x26C).as_int()

    def get_level_type_value(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114, 0x364).as_int()

    def get_level_type(self) -> LevelType:
        try:
            return LevelType.from_value(self.get_level_type_value())
        except FailedConversion:
            return LevelType.NULL

    def is_in_level(self) -> bool:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114).as_bool()

    def get_song_id(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x488, 0x1C4).as_int()

    def get_attempt(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x4A8).as_int()

    def set_attempt(self, attempt: int) -> None:
        self.write_bytes(Buffer.from_int(attempt), 0x3222D0, 0x164, 0x4A8)


number_to_resolution = {
    1: (640, 480),
    2: (720, 480),
    3: (720, 576),
    4: (800, 600),
    5: (1024, 768),
    6: (1152, 864),
    7: (1176, 644),
    8: (1280, 720),
    9: (1280, 768),
    10: (1280, 800),
    11: (1280, 960),
    12: (1280, 1024),
    13: (1360, 768),
    14: (1366, 768),
    15: (1440, 900),
    16: (1600, 900),
    17: (1600, 1024),
    18: (1680, 1050),
    19: (1768, 992),
    20: (1920, 1080),
}


def get_memory(name: str = "GeometryDash.exe", load: bool = True) -> MemoryType:
    return Memory(name, load=load)
