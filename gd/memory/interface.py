from pathlib import Path

from gd.platform import LINUX, MACOS, WINDOWS
from gd.typing import Type, TypeVar, Union

from gd.memory.data import (
    Buffer,
    Data,
    boolean,
    int8,
    uint8,
    int16,
    uint16,
    int32,
    uint32,
    int64,
    uint64,
    float32,
    float64,
    string,
    get_pointer_type,
)

from gd.memory.internal import (
    allocate_memory as system_allocate_memory,
    free_memory as system_free_memory,
    get_base_address as system_get_base_address,
    get_base_address_from_handle as system_get_base_address_from_handle,
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
    linux_open_process,
    linux_close_process,
    linux_get_process_id_from_name,
    # linux_get_process_id_from_window_title,
    linux_inject_dll,
    linux_terminate_process,
    linux_protect_process_memory,
    linux_read_process_memory,
    linux_write_process_memory,
    macos_allocate_memory,
    macos_free_memory,
    # macos_get_base_address,
    macos_get_base_address_from_handle,
    macos_open_process,
    macos_close_process,
    macos_get_process_id_from_name,
    # macos_get_process_id_from_window_title,
    macos_inject_dll,
    macos_terminate_process,
    macos_protect_process_memory,
    macos_read_process_memory,
    macos_write_process_memory,
    windows_allocate_memory,
    windows_free_memory,
    windows_get_base_address,
    # windows_get_base_address_from_handle,
    windows_open_process,
    windows_close_process,
    windows_get_process_id_from_name,
    windows_get_process_id_from_window_title,
    windows_inject_dll,
    windows_terminate_process,
    windows_protect_process_memory,
    windows_read_process_memory,
    windows_write_process_memory,
)
# from gd.memory.offsets import linux_offsets, macos_offsets, windows_offsets

__all__ = ("Address", "State", "SystemState", "LinuxState", "MacOSState", "WindowsState")

DEFAULT_WINDOW_TITLE = "Geometry Dash"
MACOS_STRING_SIZE_OFFSET = -0x18
WINDOWS_STRING_SIZE_OFFSET = 0x10

AddressT = TypeVar("AddressT", bound="Address")
T = TypeVar("T")


class SystemState:
    def __init__(
        self,
        process_name: str,
        bitness: int,
        window_title: str = DEFAULT_WINDOW_TITLE,
        load: bool = True,
    ) -> None:
        self.process_name = process_name
        self.window_title = window_title

        self.pointer_type = get_pointer_type(bitness)

        self.process_id = 0
        self.process_handle = 0
        self.base_address = 0

        self.loaded = False

        if load:
            self.load()

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

        self.process_handle = system_open_process(self.process_id)

        try:
            self.base_address = system_get_base_address_from_handle(self.process_handle)

        except NotImplementedError:
            pass

        self.base_address = system_get_base_address(self.process_id, self.process_name)

        self.loaded = True

    reload = load

    def allocate_memory(self, address: int, size: int) -> int:
        return system_allocate_memory(self.process_handle, address, size)

    def free_memory(self, address: int, size: int) -> None:
        return system_free_memory(self.process_handle, address, size)

    def protect_at(self, address: int, size: int) -> None:
        return system_protect_process_memory(self.process_handle, address, size)

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

    def read_float32(self, address: int) -> float:
        return self.read(float32, address)

    def write_float32(self, value: float, address: int) -> int:
        return self.write(float32, value, address)

    def read_float64(self, address: int) -> float:
        return self.read(float64, address)

    def write_float64(self, value: float, address: int) -> int:
        return self.write(float64, value, address)

    def get_address(self) -> "Address":
        return Address(self.base_address, self)


class LinuxState(SystemState):
    def load(self) -> None:
        self.process_id = linux_get_process_id_from_name(self.process_name)

        self.process_handle = linux_open_process(self.process_id)

        self.base_address = linux_get_base_address_from_handle(self.process_handle)

        self.loaded = True

    def allocate_memory(self, address: int, size: int) -> int:
        return linux_allocate_memory(self.process_handle, address, size)

    def free_memory(self, address: int, size: int) -> None:
        return linux_free_memory(self.process_handle, address, size)

    def protect_at(self, address: int, size: int) -> None:
        return linux_protect_process_memory(self.process_handle, address, size)

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

        self.process_handle = macos_open_process(self.process_id)

        self.base_address = macos_get_base_address_from_handle(self.process_handle)

        self.loaded = True

    def allocate_memory(self, address: int, size: int) -> int:
        return macos_allocate_memory(self.process_handle, address, size)

    def free_memory(self, address: int, size: int) -> None:
        return macos_free_memory(self.process_handle, address, size)

    def protect_at(self, address: int, size: int) -> None:
        return macos_protect_process_memory(self.process_handle, address, size)

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

        size = self.read_pointer(size_address)

        return string.from_bytes(self.read_at(address, size))

    def write_string(self, value: str, address: int) -> int:
        actual_address = address

        address = self.read_pointer(address)  # see above

        size_address = address + MACOS_STRING_SIZE_OFFSET

        previous_size = self.read_pointer(size_address)

        data = string.to_bytes(value)

        size = len(data) - 1  # account for null terminator

        if size > previous_size:
            address = self.allocate_memory(0, size)

            self.write_pointer(address, actual_address)

            size_address = address + MACOS_STRING_SIZE_OFFSET

        self.write_pointer(size, size_address)

        return self.write_at(address, data)


class WindowsState(SystemState):
    def load(self) -> None:
        try:
            self.process_id = windows_get_process_id_from_name(self.process_name)

        except LookupError:
            self.process_id = windows_get_process_id_from_window_title(self.window_title)

            if not self.process_id:
                raise

        self.process_handle = windows_open_process(self.process_id)

        self.base_address = windows_get_base_address(self.process_id, self.process_name)

        self.loaded = True

    reload = load

    def allocate_memory(self, address: int, size: int) -> int:
        return windows_allocate_memory(self.process_handle, address, size)

    def free_memory(self, address: int, size: int) -> None:
        return windows_free_memory(self.process_handle, address, size)

    def protect_at(self, address: int, size: int) -> None:
        return windows_protect_process_memory(self.process_handle, address, size)

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

        size = self.read_pointer(size_address)

        if size < WINDOWS_STRING_SIZE_OFFSET:
            try:
                return string.from_bytes(self.read_at(address, size))
            except UnicodeDecodeError:  # failed to read, let's try to interpret as a pointer
                pass

        address = self.read_pointer(address)

        return string.from_bytes(self.read_at(address, size))

    def write_string(self, value: str, address: int) -> int:
        size_address = address + WINDOWS_STRING_SIZE_OFFSET

        data = string.to_bytes(value)

        size = len(data) - 1  # account for null terminator

        self.write_pointer(size, size_address)

        if size > WINDOWS_STRING_SIZE_OFFSET:
            new_address = self.allocate_memory(0, size)

            self.write_pointer(new_address, address)

            address = new_address

        return self.write_at(address, data)


State: Type[SystemState]


if LINUX:
    State = LinuxState

elif MACOS:
    State = MacOSState

elif WINDOWS:
    State = WindowsState

else:
    State = SystemState


class Address:
    def __init__(self, address: int, state: SystemState) -> None:
        self.address = address
        self.state = state

    def add(self: AddressT, value: int) -> AddressT:
        return self.__class__(self.address + value, self.state)

    def sub(self: AddressT, value: int) -> AddressT:
        return self.__class__(self.address - value, self.state)

    def cast(self: AddressT, cls: Type[AddressT]) -> AddressT:
        return cls(self.address, self.state)

    def follow_pointer(self: AddressT) -> AddressT:
        return self.__class__(self.read_pointer(), self.state)

    def offset(self: AddressT, value: int) -> AddressT:
        return self.follow_pointer().add(value)

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
