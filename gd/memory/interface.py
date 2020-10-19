from pathlib import Path

from gd.platform import LINUX, MACOS, WINDOWS
from gd.typing import Optional, Type, TypeVar, Union, cast

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
    allocate_memory as os_allocate_memory,
    free_memory as os_free_memory,
    get_base_address as os_get_base_address,
    get_base_address_from_handle as os_get_base_address_from_handle,
    open_process as os_open_process,
    close_process as os_close_process,
    get_process_id_from_name as os_get_process_id_from_name,
    get_process_id_from_window_title as os_get_process_id_from_window_title,
    inject_dll as os_inject_dll,
    terminate_process as os_terminate_process,
    protect_process_memory as os_protect_process_memory,
    read_process_memory as os_read_process_memory,
    write_process_memory as os_write_process_memory,
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

__all__ = ("State", "OSState", "LinuxState", "MacOSState", "WindowsState")

DEFAULT_WINDOW_TITLE = "Geometry Dash"

LayerT = TypeVar("LayerT", bound="Layer")
T = TypeVar("T")


class OSState:
    GAME_MANAGER_OFFSET = 0

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
            self.process_id = os_get_process_id_from_name(self.process_name)

        except LookupError:
            self.process_id = os_get_process_id_from_window_title(self.window_title)

            if not self.process_id:
                raise

        self.process_handle = os_open_process(self.process_id)

        try:
            self.base_address = os_get_base_address_from_handle(self.process_handle)

        except NotImplementedError:
            pass

        self.base_address = os_get_base_address(self.process_id, self.process_name)

        self.loaded = True

    reload = load

    def allocate_memory(self, address: int, size: int) -> int:
        return os_allocate_memory(self.process_handle, address, size)

    def free_memory(self, address: int, size: int) -> None:
        return os_free_memory(self.process_handle, address, size)

    def protect_at(self, address: int, size: int) -> None:
        return os_protect_process_memory(self.process_handle, address, size)

    def raw_read_at(self, address: int, size: int) -> bytes:
        return os_read_process_memory(self.process_handle, address, size)

    def raw_write_at(self, address: int, data: bytes) -> int:
        return os_write_process_memory(self.process_handle, address, data)

    def inject_dll(self, path: Union[str, Path]) -> bool:
        return os_inject_dll(self.process_id, path)

    def close(self) -> None:
        return os_close_process(self.process_handle)

    def terminate(self) -> bool:
        return os_terminate_process(self.process_handle)

    # END REGION

    def read_at(self, address: int, size: int) -> Buffer:
        return Buffer(self.raw_read_at(address, size))

    def write_at(self, buffer: Buffer, address: int) -> int:
        return self.raw_write_at(address, buffer.unwrap())

    def read(self, type: Data[T], address: int) -> T:
        return type.from_bytes(self.raw_read_at(address, type.size))

    def write(self, type: Data[T], value: T, address: int) -> int:
        return self.raw_write_at(address, type.to_bytes(value))

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

    def read_string(self, address: int) -> str:
        size_address = address + string.size

        size: int = self.read_pointer(size_address)

        if size < string.size:
            try:
                return string.from_bytes(self.raw_read_at(address, size))
            except UnicodeDecodeError:  # failed to read, let's try to interpret as a pointer
                pass

        address = self.read_pointer(address)

        return string.from_bytes(self.raw_read_at(address, size))

    def write_string(self, value: str, address: int) -> None:
        size_address = address + string.size

        data = string.to_bytes(value)

        size = len(data)

        self.write_pointer(size, size_address)

        if size > string.size:
            address = self.allocate_memory(0, size)

        self.raw_write_at(address, data)

    def get_game_manager(self) -> "GameManagerLayer":
        if not self.GAME_MANAGER_OFFSET:
            raise TypeError(f"GAME_MANAGER_OFFSET not defined for {self.__class__.__name__}.")

        return GameManagerLayer(self.base_address + self.GAME_MANAGER_OFFSET, self)


class LinuxState(OSState):
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


class MacOSState(OSState):
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


class WindowsState(OSState):
    GAME_MANAGER_OFFSET = 0x3222D0

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


State: Type[OSState]


if LINUX:
    State = LinuxState

elif MACOS:
    State = MacOSState

elif WINDOWS:
    State = WindowsState

else:
    State = OSState


class Layer:
    def __init__(self, address: int, state: OSState) -> None:
        self._address = address
        self._state = state

    @property
    def address(self) -> int:
        return self._address

    @property
    def state(self) -> OSState:
        return self._state

    def compute_offset(self, offset: int) -> int:
        return self.state.read_pointer(self.address) + offset

    def offset(self, value: int, *, cls: Optional[Type[LayerT]] = None) -> LayerT:
        if cls is None:
            cls = cast(Type[LayerT], self.__class__)

        return cls(self.compute_offset(value), self.state)


class GameManagerLayer(Layer):
    def get_game_layer(self) -> "GameLayer":
        return self.offset(0x164, cls=GameLayer)


class GameLayer(Layer):
    def get_level_settings(self) -> "LevelSettingsLayer":
        return self.offset(0x22C, cls=LevelSettingsLayer)


class LevelSettingsLayer(Layer):
    def get_level(self) -> "LevelLayer":
        return self.offset(0x114, cls=LevelLayer)


class LevelLayer(Layer):
    def get_name(self) -> str:
        return self.state.read_string(self.compute_offset(0xFC))
