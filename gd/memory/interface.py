import ctypes
import itertools
import struct
import sys

try:
    from .win import get_base_address, get_handle, get_pid_from_name, read_process_memory
except Exception:  # noqa
    pass

from .enums import LevelType, Scene
from ..api.enums import SpeedConstant

from ..typing import Result, Tuple
from ..utils.text_tools import make_repr

__all__ = ("Memory", "MemoryType", "WindowsMemory", "MacOSMemory", "Result", "get_memory")


def read_until_terminator(data: bytes, terminator: int = 0) -> bytes:
    return bytes(itertools.takewhile(lambda char: char != terminator, data))


class MemoryType:
    """Pure type for Memory objects to inherit from."""

    pass


class Result:
    """Type that allows to unwrap bytes that were read into different Python types."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.order = "little"

    def __repr__(self) -> str:
        info = {"data": repr(self.to_str())}
        return make_repr(self, info)

    def with_order(self, byte_order: str) -> Result:
        self.order = byte_order
        return self

    def to_str(self) -> str:
        return " ".join(format(byte, "02x") for byte in self.data)

    def as_int(self) -> int:
        return int.from_bytes(self.data, self.order)

    def as_bool(self) -> bool:
        return self.as_int() != 0

    def as_float(self) -> float:
        if self.order == "big":
            mode = ">f"
        else:
            mode = "<f"

        try:
            return struct.unpack(mode, self.data)[0]
        except Exception as error:
            raise ValueError(f"Could not convert to float. Error: {error}.") from None

    def as_str(self, encoding: str = "utf-8", errors: str = "strict") -> str:
        return read_until_terminator(self.data).decode(encoding, errors)


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
            "base_addr": format(self.base_address, "x"),
            "handle": format(self.process_handle, "x"),
            "loaded": self.loaded,
        }
        return make_repr(self, info)

    def read_at(self, n: int = 0, address: int = 0) -> Result:
        buffer = ctypes.create_string_buffer(n)

        read_process_memory(
            self.process_handle, ctypes.c_void_p(address), ctypes.byref(buffer), n, None
        )

        return Result(buffer.raw)

    def read_bytes(self, n: int = 0, address: int = 0, *offsets) -> Result:
        address = self.base_address + address

        for offset in offsets:
            address = self.read_at(self.PTR_LEN, address).as_int() + offset

        return self.read_at(n, address)

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
        return Scene.from_value(self.get_scene_value())

    def get_resolution_value(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x2E0).as_int()

    def get_resolution(self) -> Tuple[int, int]:
        return resolution_from_value(self.get_resolution_value())

    def get_level_id_fast(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x2A0).as_int()

    def is_in_editor(self) -> bool:
        return self.read_bytes(4, 0x3222D0, 0x168).as_int() != 0

    def get_x_pos(self) -> float:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x224, 0x67C).as_float()

    def get_y_pos(self) -> float:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x224, 0x680).as_float()

    def get_speed_value(self) -> float:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x224, 0x648).as_float()

    def get_speed(self) -> SpeedConstant:
        return SpeedConstant.from_value(round(self.get_speed_value(), 1))

    def get_level_id(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x22C, 0x114, 0xF8).as_int()

    def get_level_name(self, length: int = 128) -> str:
        address = self.read_bytes(self.PTR_LEN, 0x3222D0, 0x164, 0x22C, 0x114).as_int() + 0xFC

        maybe_pointer = self.read_at(self.PTR_LEN, address).as_int()

        try:
            string = self.read_at(length, maybe_pointer).as_str()
        except UnicodeError:
            string = ""

        if not string:
            return self.read_at(length, address).as_str()
        return string

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
        return LevelType.from_value(self.get_level_type_value())

    def get_song_id(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x488, 0x1C4).as_int()

    def get_attempt(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x164, 0x4A8).as_int()


def resolution_from_value(value: int) -> Tuple[int, int]:
    mapping = {
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
    return mapping.get(value, (0, 0))


def get_memory(name: str = "GeometryDash.exe") -> MemoryType:
    return Memory(name, load=True)
