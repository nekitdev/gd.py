from abc import abstractmethod
from typing import Type, TypeVar

from attrs import define, field
from typing_extensions import Protocol

from gd.enums import Permissions, Platform
from gd.memory.context import Context
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
from gd.memory.traits import Layout, Read, Write
from gd.memory.types import Types
from gd.platform import DARWIN, WINDOWS, PlatformConfig
from gd.typing import Binary

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

T = TypeVar("T")

DEFAULT_TITLE = "Geometry Dash"

DEFAULT_SYSTEM_NAME = "Geometry Dash"
DEFAULT_DARWIN_NAME = "Geometry Dash"
DEFAULT_WINDOWS_NAME = "GeometryDash.exe"

DEFAULT_PROCESS_ID = 0
DEFAULT_HANDLE = 0
DEFAULT_BASE_ADDRESS = 0
DEFAULT_LOADED = False


class AbstractStateProtocol(Protocol):
    @abstractmethod
    def allocate_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        ...

    @abstractmethod
    def free_at(self, address: int, size: int) -> None:
        ...

    @abstractmethod
    def protect_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        ...

    @abstractmethod
    def read_at(self, address: int, size: int) -> bytes:
        ...

    @abstractmethod
    def write_at(self, address: int, data: bytes) -> None:
        ...

    @abstractmethod
    def terminate(self) -> bool:
        ...

    def allocate(self, size: int, permissions: Permissions = Permissions.DEFAULT) -> int:
        return self.allocate_at(0, size, permissions)

    def allocate_for(
        self, type: Type[Layout], permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        return self.allocate(type.size, permissions)

    def read(self, type: Type[Read[T]], address: int) -> Read[T]:
        return type.read_from(self, address)

    def read_value(self, type: Type[Read[T]], address: int) -> T:
        return type.read_value_from(self, address)

    def write(self, item: Write[T], address: int) -> None:
        item.write_to(self, address)

    def write_value(self, type: Type[Write[T]], value: T, address: int) -> None:
        type.write_value_to(self, value, address)


@define()
class AbstractState(AbstractStateProtocol):
    config: PlatformConfig
    process_name: str
    title: str = DEFAULT_TITLE
    process_id: int = DEFAULT_PROCESS_ID
    handle: int = DEFAULT_HANDLE
    base_address: int = DEFAULT_BASE_ADDRESS
    loaded: bool = DEFAULT_LOADED

    @property
    def context(self) -> Context:
        return Context(self.config)

    @property
    def types(self) -> Types:
        return Types(self.config)

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

    def ensure_loaded(self) -> None:
        if not self.is_loaded():
            self.load()

    def is_loaded(self) -> bool:
        return self.loaded


@define()
class SystemState(AbstractState):
    config: PlatformConfig = field(factory=PlatformConfig.system)

    def load(self) -> None:
        process_name = self.process_name

        try:
            process_id = system_get_process_id_from_name(process_name)

        except LookupError:
            process_id = system_get_process_id_from_title(self.title)

            if not process_id:
                raise

        self.process_id = process_id

        if not self.config.bits:
            self.config.bits = system_get_process_bits(process_id)

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
        return system_free(self.handle, address, size)

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

        if not self.config.bits:
            self.config.bits = darwin_get_process_bits(process_id)

        self.handle = handle = darwin_open(process_id)

        self.base_address = darwin_get_base_address_from_handle(handle)

        super().load()

    def allocate_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        return darwin_allocate(self.handle, address, size, permissions)

    def free_at(self, address: int, size: int) -> None:
        return darwin_free(self.handle, address, size)

    def protect_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        return darwin_protect(self.handle, address, size, permissions)

    def read_at(self, address: int, size: int) -> bytes:
        return darwin_read(self.handle, address, size)

    def write_at(self, address: int, data: bytes) -> None:
        darwin_write(self.handle, address, data)

    def terminate(self) -> bool:
        return darwin_terminate(self.handle)


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

        if not self.config.bits:
            self.config.bits = windows_get_process_bits_from_handle(handle)

        self.base_address = windows_get_base_address(process_id, process_name)

        super().load()

    def allocate_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        return windows_allocate(self.handle, address, size, permissions)

    def free_at(self, address: int, size: int) -> None:
        return windows_free(self.handle, address, size)

    def protect_at(
        self, address: int, size: int, permissions: Permissions = Permissions.DEFAULT
    ) -> int:
        return windows_protect(self.handle, address, size, permissions)

    def read_at(self, address: int, size: int) -> bytes:
        return windows_read(self.handle, address, size)

    def write_at(self, address: int, data: bytes) -> None:
        windows_write(self.handle, address, data)

    def terminate(self) -> bool:
        return windows_terminate(self.handle)


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


State: Type[AbstractState]

get_state: Binary[str, str, AbstractState]

if DARWIN:
    State = DarwinState
    get_state = get_darwin_state

elif WINDOWS:
    State = WindowsState
    get_state = get_windows_state

else:
    State = SystemState
    get_state = get_system_state
