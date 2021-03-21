# DOCUMENT

from pathlib import Path

from gd.decorators import cache_by
from gd.enums import Protection
from gd.memory.buffer import Buffer, MutBuffer, buffer, mut_buffer
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
from gd.memory.traits import Layout, Read, Write
from gd.memory.types import Types
from gd.platform import ANDROID, IOS, LINUX, MACOS, WINDOWS, Platform, system_platform
from gd.text_utils import make_repr
from gd.typing import Callable, Type, TypeVar, Union, cast

__all__ = (
    "BaseState",
    "LinuxState",
    "MacOSState",
    "SystemState",
    "WindowsState",
    "State",
    "get_linux_state",
    "get_macos_state",
    "get_system_state",
    "get_windows_state",
    "get_state",
)

T = TypeVar("T")

DEFAULT_PROTECTION = cast(Protection, Protection.READ | Protection.WRITE | Protection.EXECUTE)

DEFAULT_WINDOW_TITLE = "Geometry Dash"

DEFAULT_SYSTEM_NAME = "Geometry Dash"
DEFAULT_LINUX_NAME = "Geometry Dash"
DEFAULT_MACOS_NAME = "Geometry Dash"
DEFAULT_WINDOWS_NAME = "GeometryDash.exe"


class BaseState:
    process_name: str
    window_title: str
    bits: int
    process_id: int
    process_handle: int
    base_address: int
    loaded: bool

    platform = cast(Platform, Platform.UNKNOWN)

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
    def types(self) -> Types:
        return Types(self.bits, self.platform)

    def __repr__(self) -> str:
        info = {
            "bits": self.bits,
            "process_id": self.process_id,
            "process_handle": hex(self.process_handle),
            "base_address": hex(self.base_address),
        }

        return make_repr(self, info)

    def unload(self) -> None:
        self.process_id = 0
        self.process_handle = 0
        self.base_address = 0

        self.loaded = False

    def load(self) -> None:
        self.loaded = True

    reload = load

    def is_loaded(self) -> bool:
        return self.loaded

    # REGION: TO BE IMPLEMENTED IN SUBCLASSES

    def allocate_at(
        self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION
    ) -> int:
        raise NotImplementedError(
            "Derived classes should implement allocate_at(address, size, flags) method."
        )

    def free_at(self, address: int, size: int) -> None:
        raise NotImplementedError(
            "Derived classes should implement allocate_at(address, size) method."
        )

    def protect_at(self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION) -> int:
        raise NotImplementedError(
            "Derived classes should implement protect_at(address, size, flags) method."
        )

    def read_at(self, address: int, size: int) -> bytes:
        raise NotImplementedError("Derived classes should implement read_at(address, size) method.")

    def write_at(self, address: int, data: bytes) -> int:
        raise NotImplementedError(
            "Derived classes should implement write_at(address, size) method."
        )

    def inject_dll(self, path: Union[str, Path]) -> bool:
        raise NotImplementedError("Derived classes should implement inject_dll(path) method.")

    def close(self) -> None:
        raise NotImplementedError("Derived classes should implement close() method.")

    def terminate(self) -> bool:
        raise NotImplementedError("Derived classes should implement terminate() method.")

    # END REGION

    def read_buffer(self, size: int, address: int) -> Buffer:
        return buffer(self.read_at(address, size))

    def write_buffer(self, buffer: Buffer, address: int) -> int:
        return self.write_at(address, buffer)

    def read_mut_buffer(self, size: int, address: int) -> MutBuffer:
        return mut_buffer(self.read_at(address, size))

    def write_mut_buffer(self, mut_buffer: MutBuffer, address: int) -> int:
        return self.write_at(address, mut_buffer)

    def allocate(self, size: int, flags: Protection = DEFAULT_PROTECTION) -> int:
        return self.allocate_at(0, size, flags)

    def allocate_for(self, type: Type[Layout], flags: Protection = DEFAULT_PROTECTION) -> int:
        return self.allocate(type.size, flags)

    def read(self, type: Type[Read[T]], address: int) -> Read[T]:
        return type.read_from(self, address)

    def read_value(self, type: Type[Read[T]], address: int) -> T:
        return type.read_value_from(self, address)

    def write(self, object: Write[T], address: int) -> None:
        object.write_to(self, address)

    def write_value(self, type: Type[Write[T]], value: T, address: int) -> None:
        type.write_value_to(value, self, address)


class SystemState(BaseState):
    platform = cast(Platform, system_platform)

    def load(self) -> None:
        try:
            self.process_id = system_get_process_id_from_name(self.process_name)

        except LookupError:
            self.process_id = system_get_process_id_from_window_title(self.window_title)

            if not self.process_id:
                raise

        if not self.bits:
            self.bits = system_get_process_bits(self.process_id)

        self.process_handle = system_open_process(self.process_id)

        try:
            self.base_address = system_get_base_address_from_handle(self.process_handle)

        except NotImplementedError:
            pass

        self.base_address = system_get_base_address(self.process_id, self.process_name)

        super().load()

    reload = load

    def allocate_at(
        self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION
    ) -> int:
        return system_allocate_memory(self.process_handle, address, size, flags)

    def free_at(self, address: int, size: int) -> None:
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


class LinuxState(BaseState):
    platform = cast(Platform, Platform.LINUX)

    def load(self) -> None:
        self.process_id = linux_get_process_id_from_name(self.process_name)

        if not self.bits:
            self.bits = linux_get_process_bits(self.process_id)

        self.process_handle = linux_open_process(self.process_id)

        self.base_address = linux_get_base_address_from_handle(self.process_handle)

        super().load()

    reload = load

    def allocate_at(
        self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION
    ) -> int:
        return linux_allocate_memory(self.process_handle, address, size, flags)

    def free_at(self, address: int, size: int) -> None:
        return linux_free_memory(self.process_handle, address, size)

    def protect_at(self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION) -> int:
        return linux_protect_process_memory(self.process_handle, address, size, flags)

    def read_at(self, address: int, size: int) -> bytes:
        return linux_read_process_memory(self.process_handle, address, size)

    def write_at(self, address: int, data: bytes) -> int:
        return linux_write_process_memory(self.process_handle, address, data)

    def inject_dll(self, path: Union[str, Path]) -> bool:
        return linux_inject_dll(self.process_id, path)

    def close(self) -> None:
        return linux_close_process(self.process_handle)

    def terminate(self) -> bool:
        return linux_terminate_process(self.process_handle)


class MacOSState(BaseState):
    platform = cast(Platform, Platform.MACOS)

    def load(self) -> None:
        self.process_id = macos_get_process_id_from_name(self.process_name)

        if not self.bits:
            self.bits = macos_get_process_bits(self.process_id)

        self.process_handle = macos_open_process(self.process_id)

        self.base_address = macos_get_base_address_from_handle(self.process_handle)

        super().load()

    reload = load

    def allocate_at(
        self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION
    ) -> int:
        return macos_allocate_memory(self.process_handle, address, size, flags)

    def free_at(self, address: int, size: int) -> None:
        return macos_free_memory(self.process_handle, address, size)

    def protect_at(self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION) -> int:
        return macos_protect_process_memory(self.process_handle, address, size, flags)

    def read_at(self, address: int, size: int) -> bytes:
        return macos_read_process_memory(self.process_handle, address, size)

    def write_at(self, address: int, data: bytes) -> int:
        return macos_write_process_memory(self.process_handle, address, data)

    def inject_dll(self, path: Union[str, Path]) -> bool:
        return macos_inject_dll(self.process_id, path)

    def close(self) -> None:
        return macos_close_process(self.process_handle)

    def terminate(self) -> bool:
        return macos_terminate_process(self.process_handle)


class WindowsState(BaseState):
    platform = cast(Platform, Platform.WINDOWS)

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

        self.base_address = windows_get_base_address(self.process_id, self.process_name)

        super().load()

    reload = load

    def allocate_at(
        self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION
    ) -> int:
        return windows_allocate_memory(self.process_handle, address, size, flags)

    def free_at(self, address: int, size: int) -> None:
        return windows_free_memory(self.process_handle, address, size)

    def protect_at(self, address: int, size: int, flags: Protection = DEFAULT_PROTECTION) -> int:
        return windows_protect_process_memory(self.process_handle, address, size, flags)

    def read_at(self, address: int, size: int) -> bytes:
        return windows_read_process_memory(self.process_handle, address, size)

    def write_at(self, address: int, data: bytes) -> int:
        return windows_write_process_memory(self.process_handle, address, data)

    def inject_dll(self, path: Union[str, Path]) -> bool:
        return windows_inject_dll(self.process_id, path)

    def close(self) -> None:
        return windows_close_process(self.process_handle)

    def terminate(self) -> bool:
        return windows_terminate_process(self.process_handle)


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


State: Type[BaseState]

get_state: Callable[..., BaseState]

if ANDROID or LINUX:
    State = LinuxState
    get_state = get_linux_state

elif IOS or MACOS:
    State = MacOSState
    get_state = get_macos_state

elif WINDOWS:
    State = WindowsState
    get_state = get_windows_state

else:
    State = SystemState
    get_state = get_system_state
