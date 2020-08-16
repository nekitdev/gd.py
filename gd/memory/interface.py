import ctypes
from functools import partial
import itertools
from pathlib import Path
import struct
import sys
import time

try:
    from gd.memory.win import (
        allocate_memory,
        get_base_address,
        get_handle,
        get_pid_from_name,
        get_window_process_id,
        inject_dll,
        terminate_process,
        read_process_memory,
        write_process_memory,
    )
except Exception:  # noqa
    pass

from gd.memory.enums import Scene
from gd.api.enums import LevelType, Gamemode, SpeedConstant
from gd.typing import (
    Any,
    Buffer,
    Callable,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)
from gd.utils.converter import Converter
from gd.utils.enums import LevelDifficulty, DemonDifficulty
from gd.utils.text_tools import make_repr

__all__ = (
    "Memory",
    "MemoryType",
    "WindowsMemory",
    "MacOSMemory",
    "Buffer",
    "get_memory",
    "Bool",
    "Float32",
    "Float64",
    "Int8",
    "Int16",
    "Int32",
    "Int64",
    "UInt8",
    "UInt16",
    "UInt32",
    "UInt64",
    "String",
    "Type",
)

ORDER = {"big": ">", "little": "<"}
DEFAULT_ORDER = "little"
GAMEMODE_STATE = ("Cube", "Ship", "UFO", "Ball", "Wave", "Robot", "Spider")
NULL_BYTE = b"\x00"
T = TypeVar("T")


def read_until_terminator(data: bytes, terminator: int = 0) -> bytes:
    return bytes(itertools.takewhile(lambda char: char != terminator, data))


def list_from(one_or_seq: Union[T, Iterable[T]]) -> List[T]:
    try:
        return list(one_or_seq)
    except Exception:
        return [one_or_seq]


class MemoryType:
    """Pure type for Memory objects to inherit from."""

    pass


class BufferMeta(type):
    def __getitem__(self, byte_or_sequence: Union[int, Sequence[int]]) -> None:
        return self.from_byte_array(list_from(byte_or_sequence))


class Buffer(metaclass=BufferMeta):
    """Type that allows to unwrap bytes that were read into different Python types.

    Attributes
    ----------
    data: :class:`bytes`
        Current data that buffer works with.

    order: :class:`str`
        Represents order that buffer should interpret bits in.
        Either ``little`` for *little-endian* or ``big`` for *big-endian*.
    """

    def __init__(self, data: bytes, order: str = DEFAULT_ORDER) -> None:
        self.data = data
        self.order = order

    def __str__(self) -> str:
        return self.to_format()

    def __repr__(self) -> str:
        info = {"data": repr(self.to_format())}
        return make_repr(self, info)

    def __len__(self) -> int:
        return len(self.data)

    def with_order(self, order: str) -> Buffer:
        """Change order of the buffer to ``order`` and return ``self``."""
        self.order = order
        return self

    @classmethod
    def from_int(
        cls,
        integer: int,
        size: int = 4,
        order: str = DEFAULT_ORDER,
        signed: bool = True,
    ) -> Buffer:
        """Create buffer from an integer with size and order."""
        data = integer.to_bytes(size, order, signed=signed)
        return cls(data, order)

    def as_int(self, signed: bool = True) -> int:
        """Cast current bytes to an integer."""
        return int.from_bytes(self.data, self.order, signed=signed)

    @classmethod
    def from_bool(cls, value: bool, order: str = DEFAULT_ORDER) -> Buffer:
        """Create buffer from a boolean with order."""
        return cls.from_int(value, size=1, order=order, signed=False)

    def as_bool(self) -> bool:
        """Cast current bytes to an integer and return bool indicating if integer is non-zero."""
        return self.as_int(signed=False) != 0

    @classmethod
    def from_float(cls, number: float, order: str = DEFAULT_ORDER) -> Buffer:
        """Create buffer from a float with order. ``float`` means 32-bit floating point number."""
        mode = ORDER[order] + "f"

        try:
            data = struct.pack(mode, number)
        except Exception as error:
            raise ValueError(f"Could not convert to float. Error: {error}.") from None
        else:
            return cls(data, order)

    def as_float(self) -> float:
        """Cast current bytes to a 32-bit floating point number."""
        mode = ORDER[self.order] + "f"

        try:
            return struct.unpack(mode, self.data)[0]
        except Exception as error:
            raise ValueError(f"Could not convert from float. Error: {error}.") from None

    @classmethod
    def from_double(cls, number: float, order: str = DEFAULT_ORDER) -> Buffer:
        """Create buffer from a float with order. ``double`` means 64-bit floating point number."""
        mode = ORDER[order] + "d"

        try:
            data = struct.pack(mode, number)
        except Exception as error:
            raise ValueError(f"Could not convert from double. Error: {error}.") from None
        else:
            return cls(data, order)

    def as_double(self) -> float:
        """Cast current bytes to a 64-bit floating point number."""
        mode = ORDER[self.order] + "d"

        try:
            return struct.unpack(mode, self.data)[0]
        except Exception as error:
            raise ValueError(f"Could not convert to double. Error: {error}.") from None

    @classmethod
    def from_str(cls, string: str, terminate: bool = True, order: str = DEFAULT_ORDER) -> Buffer:
        """Create buffer from a string with order.
        If terminate is ``True``, a null byte is appended at the end.
        """
        data = string.encode()

        if terminate:
            data += NULL_BYTE

        return cls(data, order)

    def as_str(self, encoding: str = "utf-8", errors: str = "strict") -> str:
        """Interpret current bytes as a string with encoding, reading until null terminator."""
        return read_until_terminator(self.data).decode(encoding, errors)

    @classmethod
    def from_format(cls, format_str: str) -> Buffer:
        """Create buffer from byte-format string, like ``6A 14 8B CB FF``."""
        array = [int(byte, 16) for byte in format_str.split()]
        return cls.from_byte_array(array)

    def to_format(self) -> str:
        """Convert current bytes to byte-format string, like ``6A 14 8B CB FF``."""
        return " ".join(format(byte, "02X") for byte in self.data)

    @classmethod
    def from_byte_array(cls, array: Sequence[int]) -> Buffer:
        """Create buffer from a sequence of 8-bit integers."""
        return cls(bytes(array))

    def into_buffer(self) -> Any:
        """Convert current bytes to ``ctypes`` string buffer in order to write process memory."""
        return ctypes.create_string_buffer(self.data, len(self.data))


class Type:
    def __init__(
        self,
        name: str,
        size: int,
        to_bytes: Callable[[T], Buffer],
        from_bytes: Callable[[Buffer], T],
    ) -> None:
        self.name = name
        self.size = size
        self.to_bytes = to_bytes
        self.from_bytes = from_bytes

        setattr(self.__class__, self.name, self)

    def __call__(self, py_object: T) -> Buffer:
        return self.to_bytes(py_object)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{self.name}>({self.size})"


Bool = Type(name="Bool", size=1, to_bytes=Buffer.from_bool, from_bytes=Buffer.as_bool)

Float32 = Type(name="Float32", size=4, to_bytes=Buffer.from_float, from_bytes=Buffer.as_float)
Float64 = Type(name="Float64", size=8, to_bytes=Buffer.from_double, from_bytes=Buffer.as_double)

Int8 = Type(
    name="Int8",
    size=1,
    to_bytes=partial(Buffer.from_int, size=1, signed=True),
    from_bytes=partial(Buffer.as_int, signed=True),
)
Int16 = Type(
    name="Int16",
    size=2,
    to_bytes=partial(Buffer.from_int, size=2, signed=True),
    from_bytes=partial(Buffer.as_int, signed=True),
)
Int32 = Type(
    name="Int32",
    size=4,
    to_bytes=partial(Buffer.from_int, size=4, signed=True),
    from_bytes=partial(Buffer.as_int, signed=True),
)
Int64 = Type(
    name="Int64",
    size=8,
    to_bytes=partial(Buffer.from_int, size=8, signed=True),
    from_bytes=partial(Buffer.as_int, signed=True),
)

UInt8 = Type(
    name="UInt8",
    size=1,
    to_bytes=partial(Buffer.from_int, size=1, signed=False),
    from_bytes=partial(Buffer.as_int, signed=False),
)
UInt16 = Type(
    name="UInt16",
    size=2,
    to_bytes=partial(Buffer.from_int, size=2, signed=False),
    from_bytes=partial(Buffer.as_int, signed=False),
)
UInt32 = Type(
    name="UInt32",
    size=4,
    to_bytes=partial(Buffer.from_int, size=4, signed=False),
    from_bytes=partial(Buffer.as_int, signed=False),
)
UInt64 = Type(
    name="UInt64",
    size=8,
    to_bytes=partial(Buffer.from_int, size=8, signed=False),
    from_bytes=partial(Buffer.as_int, signed=False),
)

String = Type(name="String", size=16, to_bytes=Buffer.from_str, from_bytes=Buffer.as_str)


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


def add_end(string: str, part: str) -> str:
    return string if string.endswith(part) else string + part


class WindowsMemory(MemoryType):
    # [GeometryDash.exe + 0x3222D0] + 0x168 -> Editor object
    # [[[GeometryDash.exe + 0x3222D0] + 0x164] + 0x22C] + 0x114 -> Level object
    loaded = False
    process_handle = 0
    process_id = 0
    process_name = "undefined"
    base_address = 0

    def __init__(self, process_name: str, load: bool = False, ptr_type: Type = UInt32) -> None:
        self.process_name = add_end(process_name, ".exe")
        self.ptr_type = ptr_type

        if load:
            self.load()

    def __repr__(self) -> str:
        info = {
            "name": repr(self.process_name),
            "pid": self.process_id,
            "base_address": format(self.base_address, "X"),
            "handle": format(self.process_handle, "X"),
            "ptr_type": self.ptr_type,
            "loaded": self.loaded,
        }
        return make_repr(self, info)

    def resolve_layers(self, *offsets: Sequence[int], module: Optional[str] = None) -> int:
        offsets: List[int] = list_from(offsets)

        if module is None:
            address = self.base_address
        else:
            address = get_base_address(self.process_id, module)

        if offsets:
            address += offsets.pop(0)

        for offset in offsets:
            address = self.read(self.ptr_type, address) + offset

        return address

    def read_at(self, size: int = 0, address: int = 0) -> Buffer:
        """Read ``size`` bytes at ``address``, returning :class:`.Buffer` object."""
        buffer = ctypes.create_string_buffer(size)

        read_process_memory(
            self.process_handle, ctypes.c_void_p(address), ctypes.byref(buffer), size, None
        )

        return Buffer(buffer.raw)

    def read(self, type: Type, address: int = 0) -> T:
        """Read ``type`` structure at ``address``, returning :class:`.Buffer` object."""
        return type.from_bytes(self.read_at(type.size, address))

    def write_at(self, buffer: Buffer, address: int = 0) -> None:
        """Writter ``buffer`` at ``address``."""
        data = buffer.into_buffer()

        write_process_memory(
            self.process_handle, ctypes.c_void_p(address), ctypes.byref(data), len(data), None
        )

    def write(self, type: Type, value: T, address: int = 0) -> None:
        """Write ``value`` converted to ``type`` at ``address``."""
        return self.write_at(type.to_bytes(value), address)

    def read_bytes(self, size: int = 0, *offsets, module: Optional[str] = None) -> Buffer:
        """Read ``size`` bytes, resolving ``*offsets`` to the final address."""
        return self.read_at(size, self.resolve_layers(*offsets, module=module))

    def read_type(self, type: Type, *offsets, module: Optional[str] = None) -> T:
        """Read ``type``, resolving ``*offsets`` to the final address."""
        return type.from_bytes(self.read_bytes(type.size, *offsets, module=module))

    def write_bytes(self, buffer: Buffer, *offsets, module: Optional[str] = None) -> None:
        """Write ``buffer``, resolving ``*offsets`` to the final address."""
        self.write_at(buffer, self.resolve_layers(*offsets, module=module))

    def write_type(self, type: Type, value: T, *offsets, module: Optional[str] = None) -> None:
        """Write ``value`` converted to ``type``, resolving ``*offsets`` to the final address."""
        self.write_bytes(type.to_bytes(value), *offsets, module=module)

    def read_bool(self, *offsets) -> bool:
        return self.read_type(Bool, *offsets)

    def read_float32(self, *offsets) -> float:
        return self.read_type(Float32, *offsets)

    def read_float64(self, *offsets) -> float:
        return self.read_type(Float64, *offsets)

    def read_int8(self, *offsets) -> int:
        return self.read_type(Int8, *offsets)

    def read_int16(self, *offsets) -> int:
        return self.read_type(Int16, *offsets)

    def read_int32(self, *offsets) -> int:
        return self.read_type(Int32, *offsets)

    def read_int64(self, *offsets) -> int:
        return self.read_type(Int64, *offsets)

    def read_uint8(self, *offsets) -> int:
        return self.read_type(UInt8, *offsets)

    def read_uint16(self, *offsets) -> int:
        return self.read_type(UInt16, *offsets)

    def read_uint32(self, *offsets) -> int:
        return self.read_type(UInt32, *offsets)

    def read_uint64(self, *offsets) -> int:
        return self.read_type(UInt64, *offsets)

    def read_string(self, *offsets) -> str:
        """Read string resolving ``*offsets``, handling its size and where it is allocated."""
        address = self.resolve_layers(*offsets)
        size_address = address + String.size

        size = self.read(self.ptr_type, size_address)

        if size < String.size:
            try:
                return String.from_bytes(self.read_at(size, address))
            except UnicodeDecodeError:  # failed to read, let's try to interpret as a pointer
                pass

        address = self.read(self.ptr_type, address)

        return String.from_bytes(self.read_at(size, address))

    def write_bool(self, value: bool, *offsets) -> None:
        self.write_type(Bool, value, *offsets)

    def write_float32(self, value: float, *offsets) -> None:
        self.write_type(Float32, value, *offsets)

    def write_float64(self, value: float, *offsets) -> None:
        self.writr_type(Float64, value, *offsets)

    def write_int8(self, value: int, *offsets) -> None:
        self.write_type(Int8, value, *offsets)

    def write_int16(self, value: int, *offsets) -> None:
        self.write_type(Int16, value, *offsets)

    def write_int32(self, value: int, *offsets) -> None:
        self.write_type(Int32, *offsets)

    def write_int64(self, value: int, *offsets) -> None:
        self.write_type(Int64, value, *offsets)

    def write_uint8(self, value: int, *offsets) -> None:
        self.write_type(UInt8, value, *offsets)

    def write_uint16(self, value: int, *offsets) -> None:
        self.write_type(UInt16, value, *offsets)

    def write_uint32(self, value: int, *offsets) -> None:
        self.write_type(UInt32, value, *offsets)

    def write_uint64(self, value: int, *offsets) -> None:
        self.write_type(UInt64, value, *offsets)

    def write_string(self, value: str, *offsets) -> None:
        address = self.resolve_layers(*offsets)
        size_address = address + String.size

        data = String.to_bytes(value)

        size = len(data)

        self.write(self.ptr_type, size, size_address)

        if size > String.size:
            address = allocate_memory(self.process_handle, size)

        self.write_at(data, address)

    def load(self) -> None:
        """Load memory, fetching process process id, process handle and base address."""
        try:
            self.process_id = get_pid_from_name(self.process_name)

        except RuntimeError:  # not found, fallback to window check
            self.process_id = get_window_process_id("Geometry Dash")

            if not self.process_id:
                raise

        self.process_handle = get_handle(self.process_id)
        self.base_address = get_base_address(self.process_id, self.process_name)
        self.loaded = True

    def is_loaded(self) -> bool:
        """Check if memory was previously loaded."""
        return self.loaded

    def reload(self) -> None:
        """Reload memory, fetching process process id, process handle and base address."""
        self.load()

    def inject_dll(self, path: Union[str, Path]) -> bool:
        """Inject DLL from ``path`` and check if it was successfully injected."""
        return bool(inject_dll(self.process_id, path))

    def terminate(self, exit_code: int = 0) -> bool:
        return bool(terminate_process(self.process_handle, exit_code))

    def redirect_memory(self, size: int, *offsets, address: int = 0) -> None:
        """Allocate ``size`` bytes, resolve ``*offsets`` and write new address there."""
        new_address = allocate_memory(self.process_handle, size, address)
        self.write_type(self.ptr_type, new_address, *offsets)

    def get_scene_value(self) -> int:
        """Get value of current scene enum, which can be converted to :class:`.Scene`."""
        return self.read_uint32(0x3222D0, 0x1DC)

    scene_value = property(get_scene_value)

    def get_scene(self) -> Scene:
        """Get value of current scene and convert it to :class:`.Scene` enum."""
        return Scene.from_value(self.get_scene_value(), -1)

    scene = property(get_scene)

    def get_resolution_value(self) -> int:
        """Get value of current resolution."""
        return self.read_uint32(0x3222D0, 0x2E0)

    resolution_value = property(get_resolution_value)

    def get_resolution(self) -> Tuple[int, int]:
        """Get value of current resolution and try to get ``(w, h)`` tuple, ``(0, 0)`` on fail."""
        return number_to_resolution.get(self.get_resolution_value(), (0, 0))

    resolution = property(get_resolution)

    def get_gamemode_state(self) -> List[bool]:
        return list(map(bool, self.read_bytes(6, 0x3222D0, 0x164, 0x224, 0x638).data))

    gamemode_state = property(get_gamemode_state)

    def get_gamemode(self) -> Gamemode:
        try:
            value = self.get_gamemode_state().index(True) + 1
        except ValueError:  # not in the list
            value = 0

        return Gamemode.from_name(GAMEMODE_STATE[value])

    gamemode = property(get_gamemode)

    def get_level_id_fast(self) -> int:
        """Quickly read level ID, which is not always accurate for example on *official* levels."""
        return self.read_uint32(0x3222D0, 0x2A0)

    level_id_fast = property(get_level_id_fast)

    def is_in_editor(self) -> bool:
        """Check if the user is currently in editor."""
        return self.read_bool(0x3222D0, 0x168)

    def get_user_name(self) -> str:
        """Get name of the user."""
        return self.read_string(0x3222D8, 0x108)

    user_name = property(get_user_name)

    def is_dead(self) -> bool:
        """Check if the player is dead in the level."""
        return self.read_bool(0x3222D0, 0x164, 0x39C)

    def get_level_length(self) -> float:
        """Get length of the level in units."""
        return self.read_float32(0x3222D0, 0x164, 0x3B4)

    level_length = property(get_level_length)

    def get_object_count(self) -> int:
        """Get level object count."""
        return self.read_uint32(0x3222D0, 0x168, 0x3A0)

    object_count = property(get_object_count)

    def get_percent(self, *, final: float = 100.0) -> float:
        """Get current percentage in the level."""
        try:
            percent = self.get_x_pos() / self.get_level_length() * final

        except Exception:  # noqa
            percent = 0.0

        return percent if percent < final else final

    percent = property(get_percent)

    def get_x_pos(self) -> float:
        """Get X position of the player."""
        return self.read_float32(0x3222D0, 0x164, 0x224, 0x34)

    def set_x_pos(self, pos: float) -> None:
        """Set X position of the player."""
        self.write_float32(pos, 0x3222D0, 0x164, 0x224, 0x34)

    x_pos = property(get_x_pos, set_x_pos)

    def get_y_pos(self) -> float:
        """Get Y position of the player."""
        return self.read_float32(0x3222D0, 0x164, 0x224, 0x38)

    def set_y_pos(self, pos: float) -> None:
        """Set Y position of the player."""
        self.write_float32(pos, 0x3222D0, 0x164, 0x224, 0x38)

    y_pos = property(get_y_pos, set_y_pos)

    def get_speed_value(self) -> float:
        """Get value of the speed enum, which can be converted to :class:`gd.api.SpeedConstant`."""
        return self.read_float32(0x3222D0, 0x164, 0x224, 0x648)

    def set_speed_value(self, value: float) -> None:
        """Set value of the speed."""
        self.write_float32(value, 0x3222D0, 0x164, 0x224, 0x648)

    speed_value = property(get_speed_value, set_speed_value)

    def get_speed(self) -> SpeedConstant:
        """Get value of the speed and convert it to :class:`gd.api.SpeedConstant`."""
        return SpeedConstant.from_value(round(self.get_speed_value(), 1), 0)

    def set_speed(self, speed: Union[float, str, SpeedConstant], reverse: bool = False) -> None:
        """Set value of speed to ``speed``. If ``reverse``, negate given speed value."""
        speed = SpeedConstant.from_value(speed)
        value = -speed.value if reverse else speed.value

        self.set_speed_value(value)

    speed = property(get_speed, set_speed)

    def get_size(self) -> float:
        """Get hitbox size of the player icon."""
        return self.read_float32(0x3222D0, 0x164, 0x224, 0x644)

    def set_size(self, size: float) -> None:
        """Set hitbox size of the player icon."""
        self.write_float32(size, 0x3222D0, 0x164, 0x224, 0x35C)
        self.write_float32(size, 0x3222D0, 0x164, 0x224, 0x644)

    size = property(get_size, set_size)

    def is_practice_mode(self) -> bool:
        """Check whether player is in Practice Mode."""
        return self.read_bool(0x3222D0, 0x164, 0x495)

    def get_gravity(self) -> float:
        """Get value of gravity in the level. Affects cube only."""
        return self.read_float32(0x1E9050, 0)

    def set_gravity(self, gravity: float) -> None:
        """Set value of gravity in the level. Affects cube only."""
        self.redirect_memory(Float32.size, 0x1E9050)
        self.write_float32(gravity, 0x1E9050, 0)

    gravity = property(get_gravity, set_gravity)

    def get_level_id(self) -> int:
        """Get accurate ID of the level."""
        return self.read_uint32(0x3222D0, 0x164, 0x22C, 0x114, 0xF8)

    level_id = property(get_level_id)

    def get_level_name(self) -> str:
        """Get name of the level."""
        return self.read_string(0x3222D0, 0x164, 0x22C, 0x114, 0xFC)

    level_name = property(get_level_name)

    def get_level_creator(self) -> str:
        """Get creator name of the level."""
        return self.read_string(0x3222D0, 0x164, 0x22C, 0x114, 0x144)

    level_creator = property(get_level_creator)

    def get_editor_level_name(self) -> str:
        """Get level name while in editor."""
        # oh ~ zmx
        return self.read_string(0x3222D0, 0x168, 0x124, 0xEC, 0x110, 0x114, 0xFC)

    editor_level_name = property(get_editor_level_name)

    def get_level_stars(self) -> int:
        """Get amount of stars of the level."""
        return self.read_uint32(0x3222D0, 0x164, 0x22C, 0x114, 0x2AC)

    level_stars = property(get_level_stars)

    def get_level_score(self) -> int:
        """Get featured score of the level."""
        return self.read_int32(0x3222D0, 0x164, 0x22C, 0x114, 0x27C)

    level_score = property(get_level_score)

    def is_level_featured(self) -> bool:
        """Check whether the level is featured."""
        return self.get_level_score() > 0

    def is_level_epic(self) -> bool:
        """Check whether the level is epic."""
        return self.read_bool(0x3222D0, 0x164, 0x22C, 0x114, 0x280)

    def is_level_demon(self) -> bool:
        """Fetch whether the level is demon."""
        return self.read_bool(0x3222D0, 0x164, 0x22C, 0x114, 0x29C)

    def is_level_auto(self) -> bool:
        """Fetch whether the level is auto."""
        return self.read_bool(0x3222D0, 0x164, 0x22C, 0x114, 0x2B0)

    def get_level_difficulty_value(self) -> int:
        """Get difficulty value of the level, e.g. *0*, *10*, etc."""
        return self.read_uint32(0x3222D0, 0x164, 0x22C, 0x114, 0x1E4)

    level_difficulty_value = property(get_level_difficulty_value)

    def get_level_demon_difficulty_value(self) -> int:
        """Get demon difficulty value of the level, e.g. *0*, *3*, etc."""
        return self.read_uint32(0x3222D0, 0x164, 0x22C, 0x114, 0x2A0)

    level_demon_difficulty_value = property(get_level_demon_difficulty_value)

    def get_level_difficulty(self) -> Union[LevelDifficulty, DemonDifficulty]:
        """Compute actual level difficulty and return the enum."""
        address = self.read_type(self.ptr_type, 0x3222D0, 0x164, 0x22C, 0x114)

        is_demon, is_auto, difficulty, demon_difficulty = (
            self.read(Bool, address + 0x29C),
            self.read(Bool, address + 0x2B0),
            self.read(UInt32, address + 0x1E4),
            self.read(UInt32, address + 0x2A0),
        )

        return Converter.convert_level_difficulty(
            difficulty, demon_difficulty, is_demon, is_auto
        )

    level_difficulty = property(get_level_difficulty)

    def get_attempts(self) -> int:
        """Get amount of total attempts spent on the level."""
        return self.read_uint32(0x3222D0, 0x164, 0x22C, 0x114, 0x218)

    attempts = property(get_attempts)

    def get_jumps(self) -> int:
        """Get amount of total jumps spent on the level."""
        return self.read_uint32(0x3222D0, 0x164, 0x22C, 0x114, 0x224)

    jumps = property(get_jumps)

    def get_normal_percent(self) -> int:
        """Get best record in normal mode."""
        return self.read_uint32(0x3222D0, 0x164, 0x22C, 0x114, 0x248)

    normal_percent = property(get_normal_percent)

    def get_practice_percent(self) -> int:
        """Get best record in practice mode."""
        return self.read_uint32(0x3222D0, 0x164, 0x22C, 0x114, 0x26C)

    practice_percent = property(get_practice_percent)

    def get_level_type_value(self) -> int:
        """Get value of the level type, which can be converted to :class:`.LevelType`."""
        return self.read_uint32(0x3222D0, 0x164, 0x22C, 0x114, 0x364)

    level_type_value = property(get_level_type_value)

    def get_level_type(self) -> LevelType:
        """Get value of the level type, and convert it to :class:`.LevelType`."""
        return LevelType.from_value(self.get_level_type_value(), 0)

    level_type = property(get_level_type)

    def is_in_level(self) -> bool:
        """Check whether the user is currently playing a level."""
        return self.read_bool(0x3222D0, 0x164, 0x22C, 0x114)

    def get_song_id(self) -> int:
        """Get ID of the song that is used."""
        return self.read_uint32(0x3222D0, 0x164, 0x488, 0x1C4)

    song_id = property(get_song_id)

    def get_attempt(self) -> int:
        """Get current attempt number."""
        return self.read_int32(0x3222D0, 0x164, 0x4A8)

    def set_attempt(self, attempt: int) -> None:
        """Set current attempt to ``attempt``."""
        self.write_int32(attempt, 0x3222D0, 0x164, 0x4A8)

    attempt = property(get_attempt, set_attempt)

    def player_freeze(self) -> None:
        """Freeze the player."""
        self.write_bytes(Buffer[0x90, 0x90, 0x90], 0x203519)

    def player_unfreeze(self) -> None:
        """Unfreeze the player."""
        self.write_bytes(Buffer[0x50, 0xFF, 0xD6], 0x203519)

    def player_lock_jump_rotation(self) -> None:
        """Lock rotation of the cube on jump."""
        self.write_bytes(Buffer[0xC2, 0x04, 0x00], 0x1E9BF0)

    def player_unlock_jump_rotation(self) -> None:
        """Unlock rotation of the cube on jump."""
        self.write_bytes(Buffer[0x57, 0x8B, 0xF9], 0x1E9BF0)

    def player_kill_enable(self) -> None:
        """Enable player kill loop."""
        self.write_bytes(Buffer[0xE9, 0x57, 0x02, 0x00, 0x00, 0x90], 0x203DA2)
        self.write_bytes(Buffer[0xE9, 0x27, 0x02, 0x00, 0x00, 0x90], 0x20401A)

    def player_kill_disable(self) -> None:
        """Disable player kill loop."""
        self.write_bytes(Buffer[0x0F, 0x86, 0x56, 0x02, 0x00, 0x00], 0x203DA2)
        self.write_bytes(Buffer[0x0F, 0x87, 0x26, 0x02, 0x00, 0x00], 0x20401A)

    def player_kill(self) -> None:
        """Enable player kill loop and disable it after ``0.05`` seconds."""
        self.player_kill_enable()
        # wait a bit to let GD realize the change
        time.sleep(0.05)
        self.player_kill_disable()

    def enable_level_edit(self) -> None:
        """Enable hack: Level Edit."""
        self.write_bytes(Buffer[0x90, 0x90], 0x1E4A32)

    def disable_level_edit(self) -> None:
        """Disable hack: Level Edit."""
        self.write_bytes(Buffer[0x75, 0x6C], 0x1E4A32)

    def enable_accurate_percent(self) -> None:
        """Enable hack: Accurate Percentage."""
        self.write_bytes(
            Buffer[
                0xC7,
                0x02,
                0x25,
                0x66,
                0x25,
                0x25,
                0x8B,
                0x87,
                0xC0,
                0x03,
                0x00,
                0x00,
                0x8B,
                0xB0,
                0x04,
                0x01,
                0x00,
                0x00,
                0xF3,
                0x0F,
                0x5A,
                0xC0,
                0x83,
                0xEC,
                0x08,
                0xF2,
                0x0F,
                0x11,
                0x04,
                0x24,
                0x83,
                0xEC,
                0x04,
                0x89,
                0x14,
                0x24,
                0x90,
            ],
            0x208114,
        )
        self.write_bytes(Buffer[0x83, 0xC4, 0x0C], 0x20813F)

    def disable_accurate_percent(self) -> None:
        """Disable hack: Accurate Percentage."""
        self.write_bytes(
            Buffer[
                0xF3,
                0x0F,
                0x2C,
                0xC0,
                0x85,
                0xC0,
                0x0F,
                0x4F,
                0xC8,
                0xB8,
                0x64,
                0x00,
                0x00,
                0x00,
                0x3B,
                0xC8,
                0x0F,
                0x4F,
                0xC8,
                0x8B,
                0x87,
                0xC0,
                0x03,
                0x00,
                0x00,
                0x51,
                0x68,
                0x30,
                0x32,
                0x69,
                0x00,
                0x8B,
                0xB0,
                0x04,
                0x01,
                0x00,
                0x00,
            ],
            0x208114,
        )
        self.write_bytes(Buffer[0x83, 0xC4, 0x08], 0x20813F)

    def enable_level_copy(self) -> None:
        """Enable hack: Level Copy."""
        self.write_bytes(Buffer[0x90, 0x90], 0x179B8E)
        self.write_bytes(Buffer[0x8B, 0xCA, 0x90], 0x176F5C)
        self.write_bytes(Buffer[0xB0, 0x01, 0x90], 0x176FE5)

    def disable_level_copy(self) -> None:
        """Disable hack: Level Copy."""
        self.write_bytes(Buffer[0x75, 0x0E], 0x179B8E)
        self.write_bytes(Buffer[0x0F, 0x44, 0xCA], 0x176F5C)
        self.write_bytes(Buffer[0x0F, 0x95, 0xC0], 0x176FE5)

    def enable_practice_song(self) -> None:
        """Enable hack: Practice Song Bypass."""
        self.write_bytes(Buffer[0x90, 0x90, 0x90, 0x90, 0x90, 0x90], 0x20C925)
        self.write_bytes(Buffer[0x90, 0x90], 0x20D143)
        self.write_bytes(Buffer[0x90, 0x90], 0x20A563)
        self.write_bytes(Buffer[0x90, 0x90], 0x20A595)

    def disable_practice_song(self) -> None:
        """Disable hack: Practice Song Bypass."""
        self.write_bytes(Buffer[0x0F, 0x85, 0xF7, 0x00, 0x00, 0x00], 0x20C925)
        self.write_bytes(Buffer[0x75, 0x41], 0x20D143)
        self.write_bytes(Buffer[0x75, 0x3E], 0x20A563)
        self.write_bytes(Buffer[0x75, 0x0C], 0x20A595)

    def enable_noclip(self) -> None:
        """Enable hack: NoClip (*safe*)."""
        self.write_bytes(Buffer[0xE9, 0x79, 0x06, 0x00, 0x00], 0x20A23C)

    def disable_noclip(self) -> None:
        """Disable hack: NoClip."""
        self.write_bytes(Buffer[0x6A, 0x14, 0x8B, 0xCB, 0xFF], 0x20A23C)

    def enable_inf_jump(self) -> None:
        """Enable hack: Infinite Jump."""
        self.write_bytes(Buffer[0x01], 0x1E9141)
        self.write_bytes(Buffer[0x01], 0x1E9498)

    def disable_inf_jump(self) -> None:
        """Disable hack: Infinite Jump."""
        self.write_bytes(Buffer[0x00], 0x1E9141)
        self.write_bytes(Buffer[0x00], 0x1E9498)

    def disable_custom_object_limit(self) -> None:
        """Enable hack: Custom Object Limit Bypass."""
        self.write_bytes(Buffer[0xEB], 0x7A100)
        self.write_bytes(Buffer[0xEB], 0x7A022)
        self.write_bytes(Buffer[0x90, 0x90], 0x7A203)

    def enable_custom_object_limit(self) -> None:
        """Disable hack: Custom Object Limit Bypass."""
        self.write_bytes(Buffer[0x72], 0x7A100)
        self.write_bytes(Buffer[0x76], 0x7A022)
        self.write_bytes(Buffer[0x77, 0x3A], 0x7A203)

    def disable_object_limit(self) -> None:
        """Enable hack: Object Limit Bypass."""
        self.write_bytes(Buffer[0xFF, 0xFF, 0xFF, 0x7F], 0x73169)
        self.write_bytes(Buffer[0xFF, 0xFF, 0xFF, 0x7F], 0x856A4)
        self.write_bytes(Buffer[0xFF, 0xFF, 0xFF, 0x7F], 0x87B17)
        self.write_bytes(Buffer[0xFF, 0xFF, 0xFF, 0x7F], 0x87B17)
        self.write_bytes(Buffer[0xFF, 0xFF, 0xFF, 0x7F], 0x880F4)
        self.write_bytes(Buffer[0xFF, 0xFF, 0xFF, 0x7F], 0x160B06)

    def enable_object_limit(self) -> None:
        """Disable hack: Object Limit Bypass."""
        self.write_bytes(Buffer[0x80, 0x38, 0x01, 0x00], 0x73169)
        self.write_bytes(Buffer[0x80, 0x38, 0x01, 0x00], 0x856A4)
        self.write_bytes(Buffer[0x80, 0x38, 0x01, 0x00], 0x87B17)
        self.write_bytes(Buffer[0x80, 0x38, 0x01, 0x00], 0x87B17)
        self.write_bytes(Buffer[0x80, 0x38, 0x01, 0x00], 0x880F4)
        self.write_bytes(Buffer[0x80, 0x38, 0x01, 0x00], 0x160B06)

    def disable_anticheat(self) -> None:
        """Disable all AntiCheats."""
        # Speedhack kicks
        self.write_bytes(Buffer[0xEB, 0x2E], 0x202AAA)
        # Editor kick
        self.write_bytes(Buffer[0xEB], 0x15FC2E)
        # Level completion kicks
        self.write_bytes(Buffer[0xEB, 0x0C], 0x1FD557)
        self.write_bytes(
            Buffer[
                0xC7,
                0x87,
                0xE0,
                0x02,
                0x00,
                0x00,
                0x01,
                0x00,
                0x00,
                0x00,
                0xC7,
                0x87,
                0xE4,
                0x02,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x90,
                0x90,
                0x90,
                0x90,
                0x90,
                0x90,
            ],
            0x1FD742,
        )
        self.write_bytes(Buffer[0x90, 0x90, 0x90, 0x90, 0x90, 0x90], 0x1FD756)
        self.write_bytes(Buffer[0x90, 0x90, 0x90, 0x90, 0x90, 0x90], 0x1FD79A)
        self.write_bytes(Buffer[0x90, 0x90, 0x90, 0x90, 0x90, 0x90], 0x1FD7AF)
        # Level kicks
        self.write_bytes(Buffer[0x90, 0x90, 0x90, 0x90, 0x90], 0x20D3B3)
        self.write_bytes(Buffer[0x90, 0x90], 0x1FF7A2)
        # Load failed
        self.write_bytes(Buffer[0xB0, 0x01], 0x18B2B4)
        # Level reset
        self.write_bytes(Buffer[0xE9, 0xD7, 0x00, 0x00, 0x00, 0x90], 0x20C4E6)

    def enable_anticheat(self) -> None:
        """Enable all AntiCheats."""
        # Speedhack kicks
        self.write_bytes(Buffer[0x74, 0x2E], 0x202AAA)
        # Editor kick
        self.write_bytes(Buffer[0x74], 0x15FC2E)
        # Level completion kicks
        self.write_bytes(Buffer[0x74, 0x0C], 0x1FD557)
        self.write_bytes(
            Buffer[
                0x80,
                0xBF,
                0xDD,
                0x02,
                0x00,
                0x00,
                0x00,
                0x0F,
                0x85,
                0x0A,
                0xFE,
                0xFF,
                0xFF,
                0x80,
                0xBF,
                0x34,
                0x05,
                0x00,
                0x00,
                0x00,
                0x0F,
                0x84,
                0xFD,
                0xFD,
                0xFF,
                0xFF,
            ],
            0x1FD742,
        )
        self.write_bytes(Buffer[0x0F, 0x84, 0xFD, 0xFD, 0xFF, 0xFF], 0x1FD756)
        self.write_bytes(Buffer[0x0F, 0x84, 0xB9, 0xFD, 0xFF, 0xFF], 0x1FD79A)
        self.write_bytes(Buffer[0x0F, 0x85, 0xA4, 0xFD, 0xFF, 0xFF], 0x1FD7AF)
        # Level kicks
        self.write_bytes(Buffer[0xE8, 0x58, 0x04, 0x00, 0x00], 0x20D3B3)
        self.write_bytes(Buffer[0x74, 0x6E], 0x1FF7A2)
        # Load failed
        self.write_bytes(Buffer[0x74, 0x6E], 0x18B2B4)
        # Level reset
        self.write_bytes(Buffer[0x0F, 0x85, 0xD6, 0x00, 0x00, 0x00], 0x20C4E6)


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


def get_memory(name: Optional[str] = "GeometryDash", load: bool = True) -> MemoryType:
    """Create Memory object with ``name``, optionally loading it if ``load`` is ``True``."""
    return Memory(name, load=load)
