from abc import abstractmethod as required
from typing import TypeVar

from attrs import define, field
from typing_extensions import Protocol

from gd.binary_constants import (
    BOOL_SIZE,
    F32_SIZE,
    F64_SIZE,
    I8_SIZE,
    I16_SIZE,
    I32_SIZE,
    I64_SIZE,
    U8_SIZE,
    U16_SIZE,
    U32_SIZE,
    U64_SIZE,
)
from gd.binary_utils import (
    from_bool,
    from_f32,
    from_f64,
    from_i8,
    from_i16,
    from_i32,
    from_i64,
    from_u8,
    from_u16,
    from_u32,
    from_u64,
    to_bool,
    to_f32,
    to_f64,
    to_i8,
    to_i16,
    to_i32,
    to_i64,
    to_u8,
    to_u16,
    to_u32,
    to_u64,
)
from gd.enums import ByteOrder, Permissions, Platform
from gd.memory.base import StructData
from gd.memory.constants import (
    DARWIN_ACCOUNT_MANAGER_OFFSET,
    DARWIN_GAME_MANAGER_OFFSET,
    WINDOWS_ACCOUNT_MANAGER_OFFSET,
    WINDOWS_GAME_MANAGER_OFFSET,
)
from gd.memory.gd import AccountManager, GameManager
from gd.memory.internal import (
    darwin_allocate,
    darwin_free,
    darwin_get_base_address_from_handle,
    darwin_get_process_bits,
    darwin_get_process_id_from_name,
    darwin_open,
    darwin_protect,
    darwin_read,
    darwin_terminate,
    darwin_write,
    system_allocate,
    system_free,
    system_get_base_address,
    system_get_base_address_from_handle,
    system_get_process_bits,
    system_get_process_id_from_name,
    system_get_process_id_from_title,
    system_open,
    system_protect,
    system_read,
    system_terminate,
    system_write,
    windows_allocate,
    windows_free,
    windows_get_base_address,
    windows_get_process_bits_from_handle,
    windows_get_process_id_from_name,
    windows_get_process_id_from_title,
    windows_open,
    windows_protect,
    windows_read,
    windows_terminate,
    windows_write,
)
from gd.memory.pointers import Pointer
from gd.platform import DARWIN, WINDOWS, PlatformConfig

__all__ = (
    "AbstractState",
    "DarwinState",
    "SystemState",
    "WindowsState",
    "State",
    "get_darwin_state",
    "get_system_state",
    "get_windows_state",
    "get_state",
)

DEFAULT_TITLE = "Geometry Dash"

DEFAULT_SYSTEM_NAME = "Geometry Dash"
DEFAULT_DARWIN_NAME = "Geometry Dash"
DEFAULT_WINDOWS_NAME = "GeometryDash.exe"

DEFAULT_PROCESS_ID = 0
DEFAULT_HANDLE = 0
DEFAULT_BASE_ADDRESS = 0
DEFAULT_LOADED = False

NULL_POINTER = "the pointer is null"


class StateProtocol(Protocol):
    @required
    def allocate_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        ...

    @required
    def free_at(self, address: int, size: int) -> None:
        ...

    @required
    def protect_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        ...

    @required
    def read_at(self, address: int, size: int) -> bytes:
        ...

    @required
    def write_at(self, address: int, data: bytes) -> None:
        ...

    @required
    def terminate(self) -> bool:
        ...

    def allocate(self, size: int, permissions: Permissions = Permissions.DEFAULT) -> int:
        return self.allocate_at(0, size, permissions)

    def read_i8(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return from_i8(self.read_at(address, I8_SIZE), order)

    def read_u8(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return from_u8(self.read_at(address, U8_SIZE), order)

    def read_i16(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return from_i16(self.read_at(address, I16_SIZE), order)

    def read_u16(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return from_u16(self.read_at(address, U16_SIZE), order)

    def read_i32(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return from_i32(self.read_at(address, I32_SIZE), order)

    def read_u32(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return from_u32(self.read_at(address, U32_SIZE), order)

    def read_i64(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return from_i64(self.read_at(address, I64_SIZE), order)

    def read_u64(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return from_u64(self.read_at(address, U64_SIZE), order)

    def read_f32(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> float:
        return from_f32(self.read_at(address, F32_SIZE), order)

    def read_f64(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> float:
        return from_f64(self.read_at(address, F64_SIZE), order)

    def read_bool(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> bool:
        return from_bool(self.read_at(address, BOOL_SIZE), order)

    def write_i8(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_at(address, to_i8(value, order))

    def write_u8(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_at(address, to_u8(value, order))

    def write_i16(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_at(address, to_i16(value, order))

    def write_u16(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_at(address, to_u16(value, order))

    def write_i32(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_at(address, to_i32(value, order))

    def write_u32(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_at(address, to_u32(value, order))

    def write_i64(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_at(address, to_i64(value, order))

    def write_u64(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_at(address, to_u64(value, order))

    def write_f32(self, address: int, value: float, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_at(address, to_f32(value, order))

    def write_f64(self, address: int, value: float, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_at(address, to_f64(value, order))

    def write_bool(self, address: int, value: bool, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_at(address, to_bool(value, order))


AS = TypeVar("AS", bound="AbstractState")


@define()
class AbstractState(StateProtocol):
    config: PlatformConfig = field()
    process_name: str = field()
    title: str = field(default=DEFAULT_TITLE)
    process_id: int = field(default=DEFAULT_PROCESS_ID)
    handle: int = field(default=DEFAULT_HANDLE, repr=hex)
    base_address: int = field(default=DEFAULT_BASE_ADDRESS, repr=hex)
    loaded: bool = field(default=DEFAULT_LOADED)

    @property
    def bits(self) -> int:
        return self.config.bits

    @property
    def platform(self) -> Platform:
        return self.config.platform

    def unload(self) -> None:
        self.process_id = 0
        self.handle = 0
        self.base_address = 0

        self.loaded = False

    def load(self) -> None:
        self.loaded = True

    def reload(self) -> None:
        self.unload()
        self.load()

    def ensure_loaded(self: AS) -> AS:
        if not self.is_loaded():
            self.load()

        return self

    def is_loaded(self) -> bool:
        return self.loaded

    def read_isize(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        read_isize = {8: self.read_i8, 16: self.read_i16, 32: self.read_i32, 64: self.read_i64}

        return read_isize[self.bits](address, order)

    def read_usize(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        read_usize = {8: self.read_u8, 16: self.read_u16, 32: self.read_u32, 64: self.read_u64}

        return read_usize[self.bits](address, order)

    def read_byte(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return self.read_i8(address, order)

    def read_ubyte(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return self.read_u8(address, order)

    def read_short(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return self.read_i16(address, order)

    def read_ushort(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return self.read_u16(address, order)

    def read_int(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        if self.bits < 32:
            return self.read_i16(address, order)

        return self.read_i32(address, order)

    def read_uint(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        if self.bits < 32:
            return self.read_u16(address, order)

        return self.read_u32(address, order)

    def read_long(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        if self.bits > 32 and not self.platform.is_windows():
            return self.read_i64(address, order)

        return self.read_i32(address, order)

    def read_ulong(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        if self.bits > 32 and not self.platform.is_windows():
            return self.read_u64(address, order)

        return self.read_u32(address, order)

    def read_longlong(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return self.read_i64(address, order)

    def read_ulonglong(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return self.read_u64(address, order)

    def read_size(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return self.read_isize(address, order)

    def read_float(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> float:
        return self.read_f32(address, order)

    def read_double(self, address: int, order: ByteOrder = ByteOrder.NATIVE) -> float:
        return self.read_f64(address, order)

    def write_isize(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        write_isize = {8: self.write_i8, 16: self.write_i16, 32: self.write_i32, 64: self.write_i64}

        write_isize[self.bits](address, value, order)

    def write_usize(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        write_usize = {8: self.write_u8, 16: self.write_u16, 32: self.write_u32, 64: self.write_u64}

        write_usize[self.bits](address, value, order)

    def write_byte(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_i8(address, value, order)

    def write_ubyte(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_u8(address, value, order)

    def write_short(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_i16(address, value, order)

    def write_ushort(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_u16(address, value, order)

    def write_int(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        if self.bits < 32:
            self.write_i16(address, value, order)

        else:
            self.write_i32(address, value, order)

    def write_uint(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        if self.bits < 32:
            self.write_u16(address, value, order)

        else:
            self.write_u32(address, value, order)

    def write_long(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        if self.bits > 32 and not self.platform.is_windows():
            self.write_i64(address, value, order)

        else:
            self.write_i32(address, value, order)

    def write_ulong(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        if self.bits > 32 and not self.platform.is_windows():
            self.write_u64(address, value, order)

        else:
            self.write_u32(address, value, order)

    def write_longlong(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_i64(address, value, order)

    def write_ulonglong(
        self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        self.write_u64(address, value, order)

    def write_float(self, address: int, value: float, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_f32(address, value, order)

    def write_size(self, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_isize(address, value, order)

    def write_double(self, address: int, value: float, order: ByteOrder = ByteOrder.NATIVE) -> None:
        self.write_f64(address, value, order)


@define()
class SystemState(AbstractState):
    config: PlatformConfig = field(factory=PlatformConfig.system)

    def load(self) -> None:
        process_name = self.process_name

        process_id: int

        try:
            process_id = system_get_process_id_from_name(process_name)

        except LookupError:
            process_id = system_get_process_id_from_title(self.title)

            if not process_id:  # type: ignore
                raise

        self.process_id = process_id  # type: ignore

        config = self.config

        if not config.bits:
            self.config = config.with_bits(system_get_process_bits(process_id))

        self.handle = handle = system_open(process_id)

        try:
            self.base_address = system_get_base_address_from_handle(handle)

        except NotImplementedError:
            self.base_address = system_get_base_address(process_id, process_name)

        super().load()

    def allocate_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        return system_allocate(self.handle, address, size, permissions)

    def free_at(self, address: int, size: int) -> None:
        system_free(self.handle, address, size)

    def protect_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        return system_protect(self.handle, address, size, permissions)

    def read_at(self, address: int, size: int) -> bytes:
        return system_read(self.handle, address, size)

    def write_at(self, address: int, data: bytes) -> None:
        system_write(self.handle, address, data)

    def terminate(self) -> bool:
        return system_terminate(self.handle)


@define()
class DarwinState(AbstractState):
    config: PlatformConfig = field(
        factory=PlatformConfig.default_with_platform_factory(Platform.DARWIN)
    )

    def load(self) -> None:
        self.process_id = process_id = darwin_get_process_id_from_name(self.process_name)

        config = self.config

        if not config.bits:
            self.config = config.with_bits(darwin_get_process_bits(process_id))

        self.handle = handle = darwin_open(process_id)

        self.base_address = darwin_get_base_address_from_handle(handle)

        super().load()

    def allocate_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        return darwin_allocate(self.handle, address, size, permissions)  # type: ignore

    def free_at(self, address: int, size: int) -> None:
        darwin_free(self.handle, address, size)

    def protect_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        return darwin_protect(self.handle, address, size, permissions)  # type: ignore

    def read_at(self, address: int, size: int) -> bytes:
        return darwin_read(self.handle, address, size)  # type: ignore

    def write_at(self, address: int, data: bytes) -> None:
        darwin_write(self.handle, address, data)

    def terminate(self) -> bool:
        return darwin_terminate(self.handle)  # type: ignore

    @property
    def account_manager(self) -> Pointer[AccountManager]:
        return Pointer(
            self,
            self.base_address + DARWIN_ACCOUNT_MANAGER_OFFSET,
            StructData(AccountManager.reconstruct_for(self)),
        )

    @property
    def game_manager(self) -> Pointer[GameManager]:
        return Pointer(
            self,
            self.base_address + DARWIN_GAME_MANAGER_OFFSET,
            StructData(GameManager.reconstruct_for(self)),
        )


@define()
class WindowsState(AbstractState):
    config: PlatformConfig = field(
        factory=PlatformConfig.default_with_platform_factory(Platform.WINDOWS)
    )

    def load(self) -> None:
        process_name = self.process_name

        try:
            self.process_id = process_id = windows_get_process_id_from_name(process_name)

        except LookupError:
            self.process_id = process_id = windows_get_process_id_from_title(self.title)

            if not process_id:
                raise

        self.handle = handle = windows_open(process_id)

        config = self.config

        if not config.bits:
            self.config = config.with_bits(windows_get_process_bits_from_handle(handle))

        self.base_address = windows_get_base_address(process_id, process_name)

        super().load()

    def allocate_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        return windows_allocate(self.handle, address, size, permissions)  # type: ignore

    def free_at(self, address: int, size: int) -> None:
        windows_free(self.handle, address, size)

    def protect_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        return windows_protect(self.handle, address, size, permissions)  # type: ignore

    def read_at(self, address: int, size: int) -> bytes:
        return windows_read(self.handle, address, size)  # type: ignore

    def write_at(self, address: int, data: bytes) -> None:
        windows_write(self.handle, address, data)

    def terminate(self) -> bool:
        return windows_terminate(self.handle)  # type: ignore

    @property
    def account_manager(self) -> Pointer[AccountManager]:
        return Pointer(
            self,
            self.base_address + WINDOWS_ACCOUNT_MANAGER_OFFSET,
            StructData(AccountManager.reconstruct_for(self)),
        )

    @property
    def game_manager(self) -> Pointer[GameManager]:
        return Pointer(
            self,
            self.base_address + WINDOWS_GAME_MANAGER_OFFSET,
            StructData(GameManager.reconstruct_for(self)),
        )


def get_darwin_state(
    process_name: str = DEFAULT_DARWIN_NAME,
    title: str = DEFAULT_TITLE,
) -> DarwinState:
    return DarwinState(process_name=process_name, title=title)


def get_windows_state(
    process_name: str = DEFAULT_WINDOWS_NAME,
    title: str = DEFAULT_TITLE,
) -> WindowsState:
    return WindowsState(process_name=process_name, title=title)


def get_system_state(
    process_name: str = DEFAULT_SYSTEM_NAME,
    title: str = DEFAULT_TITLE,
) -> SystemState:
    return SystemState(process_name=process_name, title=title)


if DARWIN:
    State = DarwinState  # type: ignore
    get_state = get_darwin_state  # type: ignore

elif WINDOWS:
    State = WindowsState  # type: ignore
    get_state = get_windows_state  # type: ignore

else:
    State = SystemState  # type: ignore
    get_state = get_system_state  # type: ignore
