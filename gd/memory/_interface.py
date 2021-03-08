from pathlib import Path

from gd.api.editor import Editor
from gd.converters import get_actual_difficulty
from gd.crypto import unzip_level_str, zip_level_str
from gd.decorators import cache_by
from gd.enums import (
    DemonDifficulty,
    Gamemode,
    LevelDifficulty,
    LevelType,
    Protection,
    Scene,
    SpeedConstant,
)
from gd.memory._data import (
    Buffer,
    Data,
    boolean,
    float32,
    float64,
    get_pointer_type,
    get_size_type,
    int8,
    int16,
    int32,
    int64,
    string,
    uint8,
    uint16,
    uint32,
    uint64,
)
from gd.memory.internal import (
    allocate_memory as system_allocate_memory,
    free_memory as system_free_memory,
    get_base_address as system_get_base_address,
    get_base_address_from_handle as system_get_base_address_from_handle,
    get_process_bits as system_get_process_bits,
    # get_process_bits_from_handle as system_get_process_bits_from_handle,
    open_process as system_open_process,
    close_process as system_close_process,
    get_process_id_from_name as system_get_process_id_from_name,
    get_process_id_from_window_title as system_get_process_id_from_window_title,
    inject_dll as system_inject_dll,
    terminate_process as system_terminate_process,
    protect_process_memory as system_protect_process_memory,
    read_process_memory as system_read_process_memory,
    write_process_memory as system_write_process_memory,
    linux_allocate_memory,
    linux_free_memory,
    # linux_get_base_address,
    linux_get_base_address_from_handle,
    linux_get_process_bits,
    # linux_get_process_bits_from_handle,
    linux_open_process,
    linux_close_process,
    linux_get_process_id_from_name,
    # linux_get_process_id_from_window_title,
    # linux_get_process_name_from_id,
    linux_inject_dll,
    linux_terminate_process,
    linux_protect_process_memory,
    linux_read_process_memory,
    linux_write_process_memory,
    macos_allocate_memory,
    macos_free_memory,
    # macos_get_base_address,
    macos_get_base_address_from_handle,
    macos_get_process_bits,
    # macos_get_process_bits_from_handle,
    macos_open_process,
    macos_close_process,
    macos_get_process_id_from_name,
    # macos_get_process_id_from_window_title,
    # macos_get_process_name_from_id,
    macos_inject_dll,
    macos_terminate_process,
    macos_protect_process_memory,
    macos_read_process_memory,
    macos_write_process_memory,
    windows_allocate_memory,
    windows_free_memory,
    windows_get_base_address,
    # windows_get_base_address_from_handle,
    # window_get_process_bits,
    windows_get_process_bits_from_handle,
    windows_open_process,
    windows_close_process,
    windows_get_process_id_from_name,
    windows_get_process_id_from_window_title,
    windows_get_process_name_from_id,
    windows_inject_dll,
    windows_terminate_process,
    windows_protect_process_memory,
    windows_read_process_memory,
    windows_write_process_memory,
)
from gd.memory._offsets import (
    Offsets,
    linux_offsets_x32,
    linux_offsets_x64,
    macos_offsets_x32,
    macos_offsets_x64,
    offsets_x32,
    offsets_x64,
    windows_offsets_x32,
    windows_offsets_x64,
)
from gd.platform import LINUX, MACOS, WINDOWS
from gd.text_utils import is_level_probably_decoded, make_repr
from gd.typing import Callable, Dict, List, Type, TypeVar, Union, cast

__all__ = (
    "Address",
    "State",
    "SystemState",
    "LinuxState",
    "MacOSState",
    "WindowsState",
    "GameLevel",
    "get_state",
    "get_system_state",
    "get_linux_state",
    "get_macos_state",
    "get_windows_state",
)

DEFAULT_PROTECTION = cast(Protection, Protection.READ | Protection.WRITE | Protection.EXECUTE)

DEFAULT_WINDOW_TITLE = "Geometry Dash"

DEFAULT_SYSTEM_NAME = "Geometry Dash"
DEFAULT_LINUX_NAME = "Geometry Dash"
DEFAULT_MACOS_NAME = "Geometry Dash"
DEFAULT_WINDOWS_NAME = "GeometryDash.exe"

MACOS_STRING_SIZE_OFFSET = -0x18
WINDOWS_STRING_SIZE_OFFSET = 0x10

AddressT = TypeVar("AddressT", bound="Address")
AddressU = TypeVar("AddressU", bound="Address")

T = TypeVar("T")

GAMEMODE_STATE = ("Cube", "Ship", "UFO", "Ball", "Wave", "Robot", "Spider")


class SystemState:
    def __init__(
        self,
        process_name: str,
        bits: int = 0,
        window_title: str = DEFAULT_WINDOW_TITLE,
        load: bool = True,
    ) -> None:
        self.process_name = process_name
        self.window_title = window_title

        self.bits = bits
        self.process_id = 0
        self.process_handle = 0
        self.base_address = 0

        self.loaded = False

        if load:
            self.load()

    @property  # type: ignore
    @cache_by("bits")
    def byte_type(self) -> Data[int]:
        return int8

    @property  # type: ignore
    @cache_by("bits")
    def ubyte_type(self) -> Data[int]:
        return uint8

    @property  # type: ignore
    @cache_by("bits")
    def short_type(self) -> Data[int]:
        return int16

    @property  # type: ignore
    @cache_by("bits")
    def ushort_type(self) -> Data[int]:
        return uint16

    @property  # type: ignore
    @cache_by("bits")
    def int_type(self) -> Data[int]:
        if self.bits >= 32:
            return int32

        return int16

    @property  # type: ignore
    @cache_by("bits")
    def uint_type(self) -> Data[int]:
        if self.bits >= 32:
            return uint32

        return uint16

    @property  # type: ignore
    @cache_by("bits")
    def long_type(self) -> Data[int]:
        if self.bits >= 64:
            return int64

        return int32

    @property  # type: ignore
    @cache_by("bits")
    def ulong_type(self) -> Data[int]:
        if self.bits >= 64:
            return uint64

        return uint32

    @property  # type: ignore
    @cache_by("bits")
    def longlong_type(self) -> Data[int]:
        return int64

    @property  # type: ignore
    @cache_by("bits")
    def ulonglong_type(self) -> Data[int]:
        return uint64

    def __repr__(self) -> str:
        info = {
            "process_id": self.process_id,
            "process_handle": hex(self.process_handle),
            "base_address": hex(self.base_address),
            "pointer_type": self.pointer_type,
        }

        return make_repr(self, info)

    def unload(self) -> None:
        self.process_id = 0
        self.process_handle = 0
        self.base_address = 0

        self.loaded = False

    def is_loaded(self) -> bool:
        return self.loaded

    # REGION: TO BE IMPLEMENTED IN SUBCLASSES

    def load(self) -> None:
        try:
            self.process_id = system_get_process_id_from_name(self.process_name)

        except LookupError:
            self.process_id = system_get_process_id_from_window_title(self.window_title)

            if not self.process_id:
                raise

        if not self.bits:
            self.bits = system_get_process_bits(self.process_id)

        self.pointer_type = get_pointer_type(self.bits)
        self.size_type = get_size_type(self.bits)

        self.process_handle = system_open_process(self.process_id)

        try:
            self.base_address = system_get_base_address_from_handle(self.process_handle)

        except NotImplementedError:
            pass

        self.base_address = system_get_base_address(self.process_id, self.process_name)

        self.loaded = True

    reload = load

    def allocate_memory(
        self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION
    ) -> int:
        return system_allocate_memory(self.process_handle, address, size, flags)

    def free_memory(self, address: int, size: int) -> None:
        return system_free_memory(self.process_handle, address, size)

    def protect_at(self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION) -> int:
        return system_protect_process_memory(self.process_handle, address, size, flags)

    def read_at(self, address: int, size: int) -> bytes:
        return system_read_process_memory(self.process_handle, address, size)

    def write_at(self, address: int, data: bytes) -> int:
        return system_write_process_memory(self.process_handle, address, data)

    def inject_dll(self, path: Union[str, Path]) -> bool:
        return system_inject_dll(self.process_id, path)

    def close(self) -> None:
        return system_close_process(self.process_handle)

    def terminate(self) -> bool:
        return system_terminate_process(self.process_handle)

    def read_string(self, address: int) -> str:
        raise NotImplementedError("read_string(address) is not implemented in base state.")

    def write_string(self, value: str, address: int) -> int:
        raise NotImplementedError("write_string(value, address) is not implemented in base state.")

    # END REGION

    def read_buffer(self, size: int, address: int) -> Buffer:
        return Buffer(self.read_at(address, size))

    def write_buffer(self, buffer: Buffer, address: int) -> int:
        return self.write_at(address, buffer.unwrap())

    def read(self, type: Data[T], address: int) -> T:
        return type.from_bytes(self.read_at(address, type.size))

    def write(self, type: Data[T], value: T, address: int) -> int:
        return self.write_at(address, type.to_bytes(value))

    def read_pointer(self, address: int) -> int:
        return self.read(self.pointer_type, address)

    def write_pointer(self, value: int, address: int) -> int:
        return self.write(self.pointer_type, value, address)

    def read_size(self, address: int) -> int:
        return self.read(self.size_type, address)

    def write_size(self, value: int, address: int) -> int:
        return self.write(self.size_type, value, address)

    def read_bool(self, address: int) -> bool:
        return self.read(boolean, address)

    def write_bool(self, value: bool, address: int) -> int:
        return self.write(boolean, value, address)

    def read_int8(self, address: int) -> int:
        return self.read(int8, address)

    def write_int8(self, value: int, address: int) -> int:
        return self.write(int8, value, address)

    def read_uint8(self, address: int) -> int:
        return self.read(uint8, address)

    def write_uint8(self, value: int, address: int) -> int:
        return self.write(uint8, value, address)

    def read_int16(self, address: int) -> int:
        return self.read(int16, address)

    def write_int16(self, value: int, address: int) -> int:
        return self.write(int16, value, address)

    def read_uint16(self, address: int) -> int:
        return self.read(uint16, address)

    def write_uint16(self, value: int, address: int) -> int:
        return self.write(uint16, value, address)

    def read_int32(self, address: int) -> int:
        return self.read(int32, address)

    def write_int32(self, value: int, address: int) -> int:
        return self.write(int32, value, address)

    def read_uint32(self, address: int) -> int:
        return self.read(uint32, address)

    def write_uint32(self, value: int, address: int) -> int:
        return self.write(uint32, value, address)

    def read_int64(self, address: int) -> int:
        return self.read(int64, address)

    def write_int64(self, value: int, address: int) -> int:
        return self.write(int64, value, address)

    def read_uint64(self, address: int) -> int:
        return self.read(uint64, address)

    def write_uint64(self, value: int, address: int) -> int:
        return self.write(uint64, value, address)

    def read_byte(self, address: int) -> int:
        return self.read(self.byte_type, address)

    def write_byte(self, value: int, address: int) -> int:
        return self.write(self.byte_type, value, address)

    def read_ubyte(self, address: int) -> int:
        return self.read(self.ubyte_type, address)

    def write_ubyte(self, value: int, address: int) -> int:
        return self.write(self.ubyte_type, value, address)

    def read_short(self, address: int) -> int:
        return self.read(self.short_type, address)

    def write_short(self, value: int, address: int) -> int:
        return self.write(self.short_type, value, address)

    def read_ushort(self, address: int) -> int:
        return self.read(self.ushort_type, address)

    def write_ushort(self, value: int, address: int) -> int:
        return self.write(self.ushort_type, value, address)

    def read_int(self, address: int) -> int:
        return self.read(self.int_type, address)

    def write_int(self, value: int, address: int) -> int:
        return self.write(self.int_type, value, address)

    def read_uint(self, address: int) -> int:
        return self.read(self.uint_type, address)

    def write_uint(self, value: int, address: int) -> int:
        return self.write(self.uint_type, value, address)

    def read_long(self, address: int) -> int:
        return self.read(self.long_type, address)

    def write_long(self, value: int, address: int) -> int:
        return self.write(self.long_type, value, address)

    def read_ulong(self, address: int) -> int:
        return self.read(self.ulong_type, address)

    def write_ulong(self, value: int, address: int) -> int:
        return self.write(self.ulong_type, value, address)

    def read_longlong(self, address: int) -> int:
        return self.read(self.longlong_type, address)

    def write_longlong(self, value: int, address: int) -> int:
        return self.write(self.longlong_type, value, address)

    def read_ulonglong(self, address: int) -> int:
        return self.read(self.ulonglong_type, address)

    def write_ulonglong(self, value: int, address: int) -> int:
        return self.write(self.ulonglong_type, value, address)

    def read_float32(self, address: int) -> float:
        return self.read(float32, address)

    read_float = read_float32

    def write_float32(self, value: float, address: int) -> int:
        return self.write(float32, value, address)

    write_float = write_float32

    def read_float64(self, address: int) -> float:
        return self.read(float64, address)

    read_double = read_float64

    def write_float64(self, value: float, address: int) -> int:
        return self.write(float64, value, address)

    write_double = write_float64

    def get_address(self) -> "Address":
        return Address(self.base_address, self)

    address = property(get_address)

    def get_game_manager(self) -> "GameManager":
        address = self.get_address()
        return address.add_and_follow(address.offsets.game_manager.offset).cast(GameManager)

    game_manager = property(get_game_manager)

    def get_account_manager(self) -> "AccountManager":
        address = self.get_address()
        return address.add_and_follow(address.offsets.account_manager.offset).cast(AccountManager)

    account_manager = property(get_account_manager)


class LinuxState(SystemState):
    def load(self) -> None:
        self.process_id = linux_get_process_id_from_name(self.process_name)

        if not self.bits:
            self.bits = linux_get_process_bits(self.process_id)

        self.pointer_type = get_pointer_type(self.bits)
        self.size_type = get_size_type(self.bits)

        self.process_handle = linux_open_process(self.process_id)

        self.base_address = linux_get_base_address_from_handle(self.process_handle)

        self.loaded = True

    def allocate_memory(
        self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION
    ) -> int:
        return linux_allocate_memory(self.process_handle, address, size, flags)

    def free_memory(self, address: int, size: int) -> None:
        return linux_free_memory(self.process_handle, address, size)

    def protect_at(self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION) -> int:
        return linux_protect_process_memory(self.process_handle, address, size, flags)

    def raw_read_at(self, address: int, size: int) -> bytes:
        return linux_read_process_memory(self.process_handle, address, size)

    def raw_write_at(self, address: int, data: bytes) -> int:
        return linux_write_process_memory(self.process_handle, address, data)

    def inject_dll(self, path: Union[str, Path]) -> bool:
        return linux_inject_dll(self.process_id, path)

    def close(self) -> None:
        return linux_close_process(self.process_handle)

    def terminate(self) -> bool:
        return linux_terminate_process(self.process_handle)


class MacOSState(SystemState):
    def load(self) -> None:
        self.process_id = macos_get_process_id_from_name(self.process_name)

        if not self.bits:
            self.bits = macos_get_process_bits(self.process_id)

        self.pointer_type = get_pointer_type(self.bits)
        self.size_type = get_size_type(self.bits)

        self.process_handle = macos_open_process(self.process_id)

        self.base_address = macos_get_base_address_from_handle(self.process_handle)

        self.loaded = True

    def allocate_memory(
        self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION
    ) -> int:
        return macos_allocate_memory(self.process_handle, address, size, flags)

    def free_memory(self, address: int, size: int) -> None:
        return macos_free_memory(self.process_handle, address, size)

    def protect_at(self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION) -> int:
        return macos_protect_process_memory(self.process_handle, address, size, flags)

    def raw_read_at(self, address: int, size: int) -> bytes:
        return macos_read_process_memory(self.process_handle, address, size)

    def raw_write_at(self, address: int, data: bytes) -> int:
        return macos_write_process_memory(self.process_handle, address, data)

    def inject_dll(self, path: Union[str, Path]) -> bool:
        return macos_inject_dll(self.process_id, path)

    def close(self) -> None:
        return macos_close_process(self.process_handle)

    def terminate(self) -> bool:
        return macos_terminate_process(self.process_handle)

    def read_string(self, address: int) -> str:
        address = self.read_pointer(address)  # in MacOS, string is pointing to actual structure

        size_address = address + MACOS_STRING_SIZE_OFFSET

        size = self.read_size(size_address)

        return string.from_bytes(self.read_at(address, size))

    def write_string(self, value: str, address: int) -> int:
        actual_address = address

        address = self.read_pointer(address)  # see above

        size_address = address + MACOS_STRING_SIZE_OFFSET

        previous_size = self.read_size(size_address)

        data = string.to_bytes(value)

        size = len(data) - 1  # account for null terminator

        if size > previous_size:
            address = self.allocate_memory(0, size)

            self.write_pointer(address, actual_address)

            size_address = address + MACOS_STRING_SIZE_OFFSET

        self.write_size(size, size_address)

        return self.write_at(address, data)


class WindowsState(SystemState):
    def load(self) -> None:
        try:
            self.process_id = windows_get_process_id_from_name(self.process_name)

        except LookupError:
            self.process_id = windows_get_process_id_from_window_title(self.window_title)

            if not self.process_id:
                raise

            self.process_name = windows_get_process_name_from_id(self.process_id)

        self.process_handle = windows_open_process(self.process_id)

        if not self.bits:
            self.bits = windows_get_process_bits_from_handle(self.process_handle)

        self.pointer_type = get_pointer_type(self.bits)
        self.size_type = get_size_type(self.bits)

        self.base_address = windows_get_base_address(self.process_id, self.process_name)

        self.loaded = True

    reload = load

    def allocate_memory(
        self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION
    ) -> int:
        return windows_allocate_memory(self.process_handle, address, size, flags)

    def free_memory(self, address: int, size: int) -> None:
        return windows_free_memory(self.process_handle, address, size)

    def protect_at(self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION) -> int:
        return windows_protect_process_memory(self.process_handle, address, size, flags)

    def raw_read_at(self, address: int, size: int) -> bytes:
        return windows_read_process_memory(self.process_handle, address, size)

    def raw_write_at(self, address: int, data: bytes) -> int:
        return windows_write_process_memory(self.process_handle, address, data)

    def inject_dll(self, path: Union[str, Path]) -> bool:
        return windows_inject_dll(self.process_id, path)

    def close(self) -> None:
        return windows_close_process(self.process_handle)

    def terminate(self) -> bool:
        return windows_terminate_process(self.process_handle)

    def read_string(self, address: int) -> str:
        size_address = address + WINDOWS_STRING_SIZE_OFFSET

        size = self.read_size(size_address)

        if size < WINDOWS_STRING_SIZE_OFFSET:
            try:
                return string.from_bytes(self.read_at(address, size))
            except UnicodeDecodeError:  # failed to read, let's try to interpret as a pointer
                pass

        address = self.read_size(address)

        return string.from_bytes(self.read_at(address, size))

    def write_string(self, value: str, address: int) -> int:
        size_address = address + WINDOWS_STRING_SIZE_OFFSET

        data = string.to_bytes(value)

        size = len(data) - 1  # account for null terminator

        self.write_size(size, size_address)

        if size > WINDOWS_STRING_SIZE_OFFSET:
            new_address = self.allocate_memory(0, size)

            self.write_pointer(new_address, address)

            address = new_address

        return self.write_at(address, data)


def get_linux_state(
    process_name: str = DEFAULT_LINUX_NAME,
    bits: int = 0,
    window_title: str = DEFAULT_WINDOW_TITLE,
    *,
    load: bool = True,
) -> LinuxState:
    return LinuxState(process_name=process_name, bits=bits, window_title=window_title, load=load)


def get_macos_state(
    process_name: str = DEFAULT_MACOS_NAME,
    bits: int = 0,
    window_title: str = DEFAULT_WINDOW_TITLE,
    *,
    load: bool = True,
) -> MacOSState:
    return MacOSState(process_name=process_name, bits=bits, window_title=window_title, load=load)


def get_windows_state(
    process_name: str = DEFAULT_WINDOWS_NAME,
    bits: int = 0,
    window_title: str = DEFAULT_WINDOW_TITLE,
    *,
    load: bool = True,
) -> WindowsState:
    return WindowsState(process_name=process_name, bits=bits, window_title=window_title, load=load)


def get_system_state(
    process_name: str = DEFAULT_SYSTEM_NAME,
    bits: int = 0,
    window_title: str = DEFAULT_WINDOW_TITLE,
    *,
    load: bool = True,
) -> SystemState:
    return SystemState(process_name=process_name, bits=bits, window_title=window_title, load=load)


State: Type[SystemState]

get_state: Callable[..., SystemState]

if LINUX:
    State = LinuxState
    get_state = get_linux_state

elif MACOS:
    State = MacOSState
    get_state = get_macos_state

elif WINDOWS:
    State = WindowsState
    get_state = get_windows_state

else:
    State = SystemState
    get_state = get_system_state


class Address:
    OFFSETS: Dict[Type[SystemState], Dict[int, Offsets]] = {
        LinuxState: {32: linux_offsets_x32, 64: linux_offsets_x64},
        MacOSState: {32: macos_offsets_x32, 64: macos_offsets_x64},
        WindowsState: {32: windows_offsets_x32, 64: windows_offsets_x64},
        SystemState: {32: offsets_x32, 64: offsets_x64},
    }

    def __init__(self, address: int, state: SystemState) -> None:
        self.address = address
        self.state = state
        self.offsets = self.OFFSETS[type(state)][state.bits]

    def __repr__(self) -> str:
        info = {"address": hex(self.address), "state": self.state}

        return make_repr(self, info)

    def __bool__(self) -> bool:
        return bool(self.address)

    def offset(self: AddressT, *offsets) -> AddressT:
        offset_iter = iter(offsets)

        address = self

        if offsets:
            address = address.add(next(offset_iter))

        for offset in offset_iter:
            address = address.follow_and_add(offset)

        return address

    def is_null(self) -> bool:
        return not self.address

    def add(self: AddressT, value: int) -> AddressT:
        return self.__class__(self.address + value, self.state)

    def sub(self: AddressT, value: int) -> AddressT:
        return self.__class__(self.address - value, self.state)

    def cast(self: AddressT, cls: Type[AddressU]) -> AddressU:
        return cls(self.address, self.state)

    def follow_pointer(self: AddressT) -> AddressT:
        return self.__class__(self.read_pointer(), self.state)

    def follow_and_add(self: AddressT, value: int) -> AddressT:
        return self.follow_pointer().add(value)

    def follow_and_sub(self: AddressT, value: int) -> AddressT:
        return self.follow_pointer().sub(value)

    def add_and_follow(self: AddressT, value: int) -> AddressT:
        return self.add(value).follow_pointer()

    def sub_and_follow(self: AddressT, value: int) -> AddressT:
        return self.sub(value).follow_pointer()

    def protect_at(self, size: int) -> int:
        return self.state.protect_at(self.address, size)

    def read_at(self, size: int) -> bytes:
        return self.state.read_at(self.address, size)

    def write_at(self, data: bytes) -> int:
        return self.state.write_at(self.address, data)

    def read_buffer(self, size: int) -> Buffer:
        return self.state.read_buffer(size, self.address)

    def write_buffer(self, data: Buffer) -> int:
        return self.state.write_buffer(data, self.address)

    def read(self, type: Data[T]) -> T:
        return self.state.read(type, self.address)

    def write(self, type: Data[T], value: T) -> int:
        return self.state.write(type, value, self.address)

    def read_pointer(self) -> int:
        return self.state.read_pointer(self.address)

    def write_pointer(self, value: int) -> int:
        return self.state.write_pointer(value, self.address)

    def read_size(self) -> int:
        return self.state.read_size(self.address)

    def write_size(self, value: int) -> int:
        return self.state.write_size(value, self.address)

    def read_bool(self) -> bool:
        return self.state.read_bool(self.address)

    def write_bool(self, value: bool) -> int:
        return self.state.write_bool(value, self.address)

    def read_int8(self) -> int:
        return self.state.read_int8(self.address)

    def write_int8(self, value: int) -> int:
        return self.state.write_int8(value, self.address)

    def read_uint8(self) -> int:
        return self.state.read_uint8(self.address)

    def write_uint8(self, value: int) -> int:
        return self.state.write_uint8(value, self.address)

    def read_int16(self) -> int:
        return self.state.read_int16(self.address)

    def write_int16(self, value: int) -> int:
        return self.state.write_int16(value, self.address)

    def read_uint16(self) -> int:
        return self.state.read_uint16(self.address)

    def write_uint16(self, value: int) -> int:
        return self.state.write_uint16(value, self.address)

    def read_int32(self) -> int:
        return self.state.read_int32(self.address)

    def write_int32(self, value: int) -> int:
        return self.state.write_int32(value, self.address)

    def read_uint32(self) -> int:
        return self.state.read_uint32(self.address)

    def write_uint32(self, value: int) -> int:
        return self.state.write_uint32(value, self.address)

    def read_int64(self) -> int:
        return self.state.read_int64(self.address)

    def write_int64(self, value: int) -> int:
        return self.state.write_int64(value, self.address)

    def read_uint64(self) -> int:
        return self.state.read_uint64(self.address)

    def write_uint64(self, value: int) -> int:
        return self.state.write_uint64(value, self.address)

    def read_byte(self) -> int:
        return self.state.read_byte(self.address)

    def write_byte(self, value: int) -> int:
        return self.state.write_byte(value, self.address)

    def read_ubyte(self) -> int:
        return self.state.read_ubyte(self.address)

    def write_ubyte(self, value: int) -> int:
        return self.state.write_ubyte(value, self.address)

    def read_short(self) -> int:
        return self.state.read_short(self.address)

    def write_short(self, value: int) -> int:
        return self.state.write_short(value, self.address)

    def read_ushort(self) -> int:
        return self.state.read_ushort(self.address)

    def write_ushort(self, value: int) -> int:
        return self.state.write_ushort(value, self.address)

    def read_int(self) -> int:
        return self.state.read_int(self.address)

    def write_int(self, value: int) -> int:
        return self.state.write_int(value, self.address)

    def read_uint(self) -> int:
        return self.state.read_uint(self.address)

    def write_uint(self, value: int) -> int:
        return self.state.write_uint(value, self.address)

    def read_long(self) -> int:
        return self.state.read_long(self.address)

    def write_long(self, value: int) -> int:
        return self.state.write_long(value, self.address)

    def read_ulong(self) -> int:
        return self.state.read_ulong(self.address)

    def write_ulong(self, value: int) -> int:
        return self.state.write_ulong(value, self.address)

    def read_longlong(self) -> int:
        return self.state.read_longlong(self.address)

    def write_longlong(self, value: int) -> int:
        return self.state.write_longlong(value, self.address)

    def read_ulonglong(self) -> int:
        return self.state.read_ulonglong(self.address)

    def write_ulonglong(self, value: int) -> int:
        return self.state.write_ulonglong(value, self.address)

    def read_float(self) -> float:
        return self.state.read_float(self.address)

    def write_float(self, value: float) -> int:
        return self.state.write_float(value, self.address)

    def read_double(self) -> float:
        return self.state.read_double(self.address)

    def write_double(self, value: float) -> int:
        return self.state.write_double(value, self.address)

    def read_float32(self) -> float:
        return self.state.read_float32(self.address)

    def write_float32(self, value: float) -> int:
        return self.state.write_float32(value, self.address)

    def read_float64(self) -> float:
        return self.state.read_float64(self.address)

    def write_float64(self, value: float) -> int:
        return self.state.write_float64(value, self.address)

    def read_string(self) -> str:
        return self.state.read_string(self.address)

    def write_string(self, value: str) -> int:
        return self.state.write_string(value, self.address)


class GameManager(Address):
    def get_scene_value(self) -> int:
        return self.add(self.offsets.game_manager.scene).read_uint()

    scene_value = property(get_scene_value)

    def get_scene(self) -> Scene:
        return Scene.from_value(self.scene_value, -1)

    scene = property(get_scene)

    def get_play_layer(self) -> "PlayLayer":
        return self.add_and_follow(self.offsets.game_manager.play_layer).cast(PlayLayer)

    play_layer = property(get_play_layer)

    def get_editor_layer(self) -> "EditorLayer":
        return self.add_and_follow(self.offsets.game_manager.editor_layer).cast(EditorLayer)

    editor_layer = property(get_editor_layer)


class AccountManager(Address):
    def get_password(self) -> str:
        return self.add(self.offsets.account_manager.password).read_string()

    def set_password(self, value: str) -> None:
        self.add(self.offsets.account_manager.password).write_string(value)

    password = property(get_password, set_password)

    def get_user_name(self) -> str:
        return self.add(self.offsets.account_manager.user_name).read_string()

    def set_user_name(self, value: str) -> None:
        self.add(self.offsets.account_manager.user_name).write_string(value)

    user_name = property(get_user_name, set_user_name)


class BaseGameLayer(Address):
    def get_player(self) -> "Player":
        return self.add_and_follow(self.offsets.base_game_layer.player).cast(Player)

    player = property(get_player)

    def get_level_settings(self) -> "LevelSettingsLayer":
        return self.add_and_follow(self.offsets.base_game_layer.level_settings).cast(
            LevelSettingsLayer
        )

    level_settings = property(get_level_settings)


class PlayLayer(BaseGameLayer):
    def get_practice_mode(self) -> bool:
        return self.add(self.offsets.play_layer.practice_mode).read_bool()

    practice_mode = property(get_practice_mode)

    def is_practice_mode(self) -> bool:
        return self.practice_mode

    def get_attempt(self) -> int:
        return self.add(self.offsets.play_layer.attempt).read_int()

    def set_attempt(self, value: int) -> None:
        self.add(self.offsets.play_layer.attempt).write_int(value)

    attempt = property(get_attempt, set_attempt)

    def get_dead(self) -> bool:
        return self.add(self.offsets.play_layer.dead).read_bool()

    dead = property(get_dead)

    def is_dead(self) -> bool:
        return self.dead

    def get_level_length(self) -> float:
        return self.add(self.offsets.play_layer.level_length).read_float()

    def set_level_length(self, value: float) -> None:
        self.add(self.offsets.play_layer.level_length).read_float()

    level_length = property(get_level_length, set_level_length)

    def get_percent(self, total: float = 100.0) -> float:
        level_length = self.level_length

        if level_length:
            player = self.player

            if player.is_null():
                return 0.0

            result = player.x / level_length * total

            return result if result < total else total

        return 0.0

    percent = property(get_percent)


class EditorLayer(BaseGameLayer):
    def get_object_count(self) -> int:
        return self.add(self.offsets.editor_layer.object_count).read_uint()

    object_count = property(get_object_count)


class LevelSettingsLayer(Address):
    def get_level(self) -> "GameLevel":
        return self.add_and_follow(self.offsets.level_settings.level).cast(GameLevel)

    level = property(get_level)


class Player(Address):
    def get_gamemodes(self) -> List[bool]:
        return list(map(bool, self.add(self.offsets.player.gamemodes).read_at(6)))

    def set_gamemodes(self, gamemodes: List[bool]) -> None:
        self.add(self.offsets.player.gamemodes).write_buffer(Buffer.from_byte_array(gamemodes))

    gamemodes = property(get_gamemodes, set_gamemodes)

    def get_gamemode(self) -> Gamemode:
        try:
            index = self.gamemodes.index(True) + 1

        except ValueError:
            index = 0

        return Gamemode.from_name(GAMEMODE_STATE[index])

    def set_gamemode(self, gamemode: Union[int, str, Gamemode]) -> None:
        gamemodes = [False, False, False, False, False, False]

        try:
            index = GAMEMODE_STATE.index(Gamemode.from_value(gamemode).title)

        except ValueError:
            pass

        else:
            gamemodes[index] = True

        self.gamemodes = gamemodes

    gamemode = property(get_gamemode, set_gamemode)

    def get_flipped_gravity(self) -> bool:
        return self.add(self.offsets.player.flipped_gravity).read_bool()

    def set_flipped_gravity(self, value: bool) -> None:
        self.add(self.offsets.player.flipped_gravity).write_bool(value)

    flipped_gravity = property(get_flipped_gravity, set_flipped_gravity)

    def flip_gravity(self) -> None:
        self.flipped_gravity = not self.flipped_gravity

    def get_size(self) -> float:
        return self.add(self.offsets.player.size).read_float()

    def set_size(self, value: float) -> None:
        self.add(self.offsets.player.size).write_float(value)

    size = property(get_size, set_size)

    def get_speed_value(self) -> float:
        return self.add(self.offsets.player.speed).read_float()

    def set_speed_value(self, value: float) -> None:
        self.add(self.offsets.player.speed).write_float(value)

    speed_value = property(get_speed_value, set_speed_value)

    def get_speed(self) -> SpeedConstant:
        return SpeedConstant.from_value(self.speed_value)

    def set_speed(self, value: Union[float, str, SpeedConstant], reverse: bool = False) -> None:
        speed_value = SpeedConstant.from_value(value).value

        if reverse:
            speed_value = -speed_value

        self.speed_value = speed_value

    speed = property(get_speed, set_speed)

    def get_x(self) -> float:
        return self.add(self.offsets.node.x).read_float()

    def set_x(self, value: float) -> None:
        self.add(self.offsets.node.x).write_float(value)

    x = property(get_x, set_x)

    def get_y(self) -> float:
        return self.add(self.offsets.node.y).read_float()

    def set_y(self, value: float) -> None:
        self.add(self.offsets.node.y).write_float(value)

    y = property(get_y, set_y)


class GameLevel(Address):
    def get_id(self) -> int:
        return self.add(self.offsets.level.id).read_uint()

    def set_id(self, value: int) -> None:
        self.add(self.offsets.level.id).write_uint(value)

    id = property(get_id, set_id)

    def get_name(self) -> str:
        return self.add(self.offsets.level.name).read_string()

    def set_name(self, value: str) -> None:
        self.add(self.offsets.level.name).write_string(value)

    name = property(get_name, set_name)

    def get_unprocessed_data(self) -> str:
        return self.add(self.offsets.level.unprocessed_data).read_string()

    def set_unprocessed_data(self, value: str) -> None:
        self.add(self.offsets.level.unprocessed_data).write_string(value)

    unprocessed_data = property(get_unprocessed_data, set_unprocessed_data)

    @cache_by("unprocessed_data")
    def get_data(self) -> str:
        unprocessed_data = self.unprocessed_data

        if is_level_probably_decoded(unprocessed_data):
            return unprocessed_data

        else:
            return unzip_level_str(unprocessed_data)

    def set_data(self, data: str) -> None:
        if is_level_probably_decoded(data):
            self.unprocessed_data = zip_level_str(data)

        else:
            self.unprocessed_data = data

    data = property(get_data, set_data)

    def open_editor(self) -> Editor:
        return Editor.load_from(self, "data")

    def get_description(self) -> str:
        return self.add(self.offsets.level.description).read_string()

    def set_description(self, value: str) -> None:
        self.add(self.offsets.level.description).write_string(value)

    description = property(get_description, set_description)

    def get_creator_name(self) -> str:
        return self.add(self.offsets.level.creator_name).read_string()

    def set_creator_name(self, value: str) -> None:
        self.add(self.offsets.level.creator_name).write_string(value)

    creator_name = property(get_creator_name, set_creator_name)

    def get_difficulty_numerator(self) -> int:
        return self.add(self.offsets.level.difficulty_numerator).read_uint()

    def set_difficulty_numerator(self, value: int) -> None:
        self.add(self.offsets.level.difficulty_numerator).write_uint(value)

    difficulty_numerator = property(get_difficulty_numerator, set_difficulty_numerator)

    def get_difficulty_denominator(self) -> int:
        return self.add(self.offsets.level.difficulty_denominator).read_uint()

    def set_difficulty_denominator(self, value: int) -> None:
        self.add(self.offsets.level.difficulty_denominator).write_uint(value)

    difficulty_denominator = property(get_difficulty_denominator, set_difficulty_denominator)

    @property
    def level_difficulty(self) -> int:
        if self.difficulty_denominator:
            return self.difficulty_numerator // self.difficulty_denominator

        return 0

    def get_attempts(self) -> int:
        return self.add(self.offsets.level.attempts).read_uint()

    def set_attempts(self, value: int) -> None:
        self.add(self.offsets.level.attempts).write_uint(value)

    attempts = property(get_attempts, set_attempts)

    def get_jumps(self) -> int:
        return self.add(self.offsets.level.jumps).read_uint()

    def set_jumps(self, value: int) -> None:
        self.add(self.offsets.level.jumps).write_uint(value)

    jumps = property(get_jumps, set_jumps)

    def get_normal_percent(self) -> int:
        return self.add(self.offsets.level.normal_percent).read_uint()

    def set_normal_percent(self, value: int) -> None:
        self.add(self.offsets.level.normal_percent).write_uint(value)

    normal_percent = property(get_normal_percent, set_normal_percent)

    def get_practice_percent(self) -> int:
        return self.add(self.offsets.level.practice_percent).read_uint()

    def set_practice_percent(self, value: int) -> None:
        self.add(self.offsets.level.practice_percent).write_uint(value)

    practice_percent = property(get_practice_percent, set_practice_percent)

    def get_score(self) -> int:
        return self.add(self.offsets.level.score).read_int()

    def set_score(self, value: int) -> None:
        self.add(self.offsets.level.score).write_int(value)

    score = property(get_score, set_score)

    def is_featured(self) -> bool:
        return self.score > 0

    def was_unfeatured(self) -> bool:
        return self.score < 0

    def get_epic(self) -> bool:
        return self.add(self.offsets.level.epic).read_bool()

    def set_epic(self, value: bool) -> None:
        self.add(self.offsets.level.epic).write_bool(value)

    epic = property(get_epic, set_epic)

    def is_epic(self) -> bool:
        return self.epic

    def get_demon(self) -> bool:
        return self.add(self.offsets.level.demon).read_bool()

    def set_demon(self, value: bool) -> None:
        self.add(self.offsets.level.demon).write_bool(value)

    demon = property(get_demon, set_demon)

    def is_demon(self) -> bool:
        return self.demon

    def get_demon_difficulty(self) -> int:
        return self.add(self.offsets.level.demon_difficulty).read_uint()

    def set_demon_difficulty(self, value: int) -> None:
        self.add(self.offsets.level.demon_difficulty).write_uint(value)

    demon_difficulty = property(get_demon_difficulty, set_demon_difficulty)

    def get_stars(self) -> int:
        return self.add(self.offsets.level.stars).read_uint()

    def set_stars(self, value: int) -> None:
        self.add(self.offsets.level.stars).write_uint(value)

    stars = property(get_stars, set_stars)

    def is_rated(self) -> bool:
        return self.stars > 0

    def get_auto(self) -> bool:
        return self.add(self.offsets.level.auto).read_bool()

    def set_auto(self, value: bool) -> None:
        self.add(self.offsets.level.auto).write_bool(value)

    auto = property(get_auto, set_auto)

    def is_auto(self) -> bool:
        return self.auto

    def get_difficulty(self) -> Union[LevelDifficulty, DemonDifficulty]:
        return get_actual_difficulty(
            level_difficulty=self.level_difficulty,
            demon_difficulty=self.demon_difficulty,
            is_auto=self.is_auto(),
            is_demon=self.is_demon(),
        )

    def set_difficulty(self, difficulty: Union[LevelDifficulty, DemonDifficulty]) -> None:
        ...

    difficulty = property(get_difficulty, set_difficulty)

    def get_level_type_value(self) -> int:
        return self.add(self.offsets.level.level_type).read_uint()

    def set_level_type_value(self, value: int) -> None:
        self.add(self.offsets.level.level_type).write_uint(value)

    level_type_value = property(get_level_type_value, set_level_type_value)

    def get_level_type(self) -> LevelType:
        return LevelType.from_value(self.level_type_value, 0)

    def set_level_type(self, level_type: Union[int, str, LevelType]) -> None:
        self.level_type_value = LevelType.from_value(level_type).value

    level_type = property(get_level_type, set_level_type)
