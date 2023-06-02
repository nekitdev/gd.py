# type: ignore  # XXX: we need to be extremely careful here

import ctypes
from pathlib import Path
from types import TracebackType as Traceback
from typing import Generator, Optional, Type, TypeVar

from attrs import frozen
from typing_aliases import AnyError
from typing_extensions import TypeAlias, final

from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.enums import Permissions
from gd.memory.internal import unimplemented
from gd.memory.internal.utils import Struct, external
from gd.platform import SYSTEM_BITS
from gd.string_utils import tick

__all__ = (
    "open",
    "close",
    "terminate",
    "allocate",
    "free",
    "protect",
    "read",
    "write",
    "get_base_address",
    "get_base_address_from_handle",
    "get_process_bits",
    "get_process_bits_from_handle",
    "get_process_id_from_name",
    "get_process_id_from_title",
)

CAN_NOT_DEFINE_INTERNAL_FUNCTIONS_FOR_WINDOWS = "can not define internal functions for windows"

try:
    from ctypes import wintypes

except ValueError:
    raise ImportError(CAN_NOT_DEFINE_INTERNAL_FUNCTIONS_FOR_WINDOWS) from None

try:
    ctypes.WinDLL

except AttributeError:
    raise ImportError(CAN_NOT_DEFINE_INTERNAL_FUNCTIONS_FOR_WINDOWS) from None

KERNEL_DLL = "kernel32.dll"
USER_DLL = "user32.dll"

try:
    KERNEL = ctypes.WinDLL(KERNEL_DLL)
    USER = ctypes.WinDLL(USER_DLL)

except OSError:
    raise ImportError(CAN_NOT_DEFINE_INTERNAL_FUNCTIONS_FOR_WINDOWS) from None


MAX_MODULE_NAME = 0xFF

MEMORY_RESERVE = 0x1000
MEMORY_COMMIT = 0x2000
MEMORY_RELEASE = 0x8000

PAGE_NO_ACCESS = 0x01
PAGE_READ_ONLY = 0x02
PAGE_READ_WRITE = 0x04

PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READ_WRITE = 0x40

NONE = Permissions.NONE
READ = Permissions.READ
WRITE = Permissions.WRITE
EXECUTE = Permissions.EXECUTE

PERMISSIONS = {  # closest approximations
    NONE: PAGE_NO_ACCESS,
    READ: PAGE_READ_ONLY,
    WRITE: PAGE_READ_WRITE,
    EXECUTE: PAGE_EXECUTE,
    READ | WRITE: PAGE_READ_WRITE,
    READ | EXECUTE: PAGE_EXECUTE_READ,
    WRITE | EXECUTE: PAGE_EXECUTE_READ_WRITE,
    READ | WRITE | EXECUTE: PAGE_EXECUTE_READ_WRITE,
}

PROCESS_ALL_ACCESS = 0x100000 | 0x0F0000 | 0x000FFF

SNAP_PROCESS = 0x02

SNAP_MODULE = 0x08
SNAP_MODULE_32 = 0x10

ULONG_POINTER: TypeAlias = ctypes.POINTER(wintypes.ULONG)

CHAR_MAX_PATH: TypeAlias = wintypes.CHAR * wintypes.MAX_PATH


class ProcessEntry(Struct):
    size: wintypes.DWORD
    count_usage: wintypes.DWORD
    process_id: wintypes.DWORD
    default_heap_id: ULONG_POINTER
    module_id: wintypes.DWORD
    count_threads: wintypes.DWORD
    parent_process_id: wintypes.DWORD
    base_priority: wintypes.LONG
    flags: wintypes.DWORD
    exe_file: CHAR_MAX_PATH

    @property
    def id(self) -> int:
        return self.process_id

    @property
    def name(self) -> str:
        return self.exe_file.decode(DEFAULT_ENCODING, DEFAULT_ERRORS)

    def __init__(self) -> None:
        self.size = ctypes.sizeof(self)


LP_PROCESS_ENTRY = ctypes.POINTER(ProcessEntry)

MAX_MODULE_NAME_NULL = MAX_MODULE_NAME + 1

BYTE_POINTER: TypeAlias = ctypes.POINTER(wintypes.BYTE)

CHAR_MAX_MODULE_NAME: TypeAlias = wintypes.CHAR * MAX_MODULE_NAME_NULL


class ModuleEntry(Struct):
    size: wintypes.DWORD
    module_id: wintypes.DWORD
    process_id: wintypes.DWORD
    global_count_usage: wintypes.DWORD
    proc_count_usage: wintypes.DWORD
    module_base_address: BYTE_POINTER
    module_base_size: wintypes.DWORD
    module_handle: wintypes.HMODULE
    module_name: CHAR_MAX_MODULE_NAME
    exe_path: CHAR_MAX_PATH

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.size = ctypes.sizeof(self)

    @property
    def base_address(self) -> int:
        return ctypes.addressof(self.module_base_address.contents)

    @property
    def name(self) -> str:
        return self.module_name.decode(DEFAULT_ENCODING, DEFAULT_ERRORS)

    @property
    def path(self) -> Path:
        return Path(self.exe_path.decode(DEFAULT_ENCODING, DEFAULT_ERRORS))


LP_MODULE_ENTRY = ctypes.POINTER(ModuleEntry)


class SecurityAttributes(Struct):
    length: wintypes.DWORD
    security_descriptor: wintypes.LPVOID
    inherit_handle: wintypes.BOOL

    def __init__(self) -> None:
        self.length = ctypes.sizeof(self)


LP_SECURITY_ATTRIBUTES = ctypes.POINTER(SecurityAttributes)


@external(KERNEL.CreateToolhelp32Snapshot)
def _create_snapshot(flags: wintypes.DWORD, process_id: wintypes.DWORD) -> wintypes.HANDLE:
    ...


@external(KERNEL.Process32First)
def _process_first(handle: wintypes.HANDLE, entry_pointer: LP_PROCESS_ENTRY) -> wintypes.BOOL:
    ...


@external(KERNEL.Process32Next)
def _process_next(handle: wintypes.HANDLE, entry_pointer: LP_PROCESS_ENTRY) -> wintypes.BOOL:
    ...


@external(KERNEL.Module32First)
def _module_first(handle: wintypes.HANDLE, entry_pointer: LP_MODULE_ENTRY) -> wintypes.BOOL:
    ...


@external(KERNEL.Module32Next)
def _module_next(handle: wintypes.HANDLE, entry_pointer: LP_MODULE_ENTRY) -> wintypes.BOOL:
    ...


@external(KERNEL.CloseHandle)
def _close_handle(handle: wintypes.HANDLE) -> wintypes.BOOL:
    ...


@external(KERNEL.OpenProcess)
def _open_process(
    access: wintypes.DWORD, inherit_handle: wintypes.BOOL, process_id: wintypes.DWORD
) -> wintypes.HANDLE:
    ...


@external(KERNEL.ReadProcessMemory)
def _read_process_memory(
    handle: wintypes.HANDLE,
    base_address: wintypes.LPVOID,
    buffer: wintypes.LPCVOID,
    size: ctypes.c_size_t,
    size_ptr: ctypes.POINTER(ctypes.c_size_t),
) -> wintypes.BOOL:
    ...


@external(KERNEL.WriteProcessMemory)
def _write_process_memory(
    handle: wintypes.HANDLE,
    base_address: wintypes.LPVOID,
    buffer: wintypes.LPCVOID,
    size: ctypes.c_size_t,
    size_ptr: ctypes.POINTER(ctypes.c_size_t),
) -> wintypes.BOOL:
    ...


@external(KERNEL.VirtualAllocEx)
def _virtual_alloc(
    handle: wintypes.HANDLE,
    address: wintypes.LPVOID,
    size: ctypes.c_size_t,
    allocation_type: wintypes.DWORD,
    protect: wintypes.DWORD,
) -> wintypes.LPVOID:
    ...


@external(KERNEL.VirtualFreeEx)
def _virtual_free(
    handle: wintypes.HANDLE,
    address: wintypes.LPVOID,
    size: ctypes.c_size_t,
    free_type: wintypes.DWORD,
) -> wintypes.BOOL:
    ...


@external(KERNEL.TerminateProcess)
def _terminate_process(handle: wintypes.HANDLE, exit_code: wintypes.UINT) -> wintypes.BOOL:
    ...


@external(USER.FindWindowA)
def _find_window(class_name: wintypes.LPCSTR, title: wintypes.LPCSTR) -> wintypes.HWND:
    ...


@external(USER.GetWindowThreadProcessId)
def _get_window_process_id(
    handle: wintypes.HWND, process_id_ptr: wintypes.LPDWORD
) -> wintypes.DWORD:
    ...


@external(KERNEL.GetModuleHandleA)
def _get_module_handle(module_name: wintypes.LPCSTR) -> wintypes.HMODULE:
    ...


@external(KERNEL.GetProcAddress)
def _get_proc_address(
    module_handle: wintypes.HMODULE, proc_name: wintypes.LPCSTR
) -> wintypes.LPVOID:
    ...


@external(KERNEL.VirtualProtectEx)
def _virtual_protect(
    handle: wintypes.HANDLE,
    address: wintypes.LPVOID,
    size: ctypes.c_size_t,
    flags: wintypes.DWORD,
    old_protect: wintypes.PDWORD,
) -> wintypes.BOOL:
    ...


@external(KERNEL.IsWow64Process)
def _is_wow_64_process_via_pointer(
    handle: wintypes.HANDLE, bool_ptr: wintypes.PBOOL
) -> wintypes.BOOL:
    pass


E = TypeVar("E", bound=AnyError)


@final
@frozen()
class _CloseHandleManager:
    _handle: int

    def __enter__(self) -> int:
        return self._handle

    def __exit__(
        self, error_type: Optional[Type[E]], error: Optional[E], traceback: Optional[Traceback]
    ) -> None:
        _close_handle(self._handle)


def _close_handle_manager(handle: int) -> _CloseHandleManager:
    return _CloseHandleManager(handle)


def _iter_processes() -> Generator[ProcessEntry, None, None]:
    process_snapshot = _create_snapshot(SNAP_PROCESS, 0)

    process_entry = ProcessEntry()

    process = _process_first(process_snapshot, ctypes.byref(process_entry))

    with _close_handle_manager(process_snapshot):
        while process:
            yield process_entry
            process = _process_next(process_snapshot, ctypes.byref(process_entry))


def _iter_modules(process_id: int) -> Generator[ModuleEntry, None, None]:
    module_snapshot = _create_snapshot(SNAP_MODULE | SNAP_MODULE_32, process_id)

    module_entry = ModuleEntry()

    module = _module_first(module_snapshot, ctypes.byref(module_entry))

    with _close_handle_manager(module_snapshot):
        while module:
            yield module_entry
            module = _module_next(module_snapshot, ctypes.byref(module_entry))


def _is_wow_64_process(handle: int) -> bool:
    result = wintypes.BOOL(0)

    _is_wow_64_process_via_pointer(handle, ctypes.byref(result))

    return bool(result.value)


def get_process_bits(process_id: int) -> int:
    with _close_handle_manager(open(process_id)) as handle:
        return get_process_bits_from_handle(handle)


def get_process_bits_from_handle(handle: int) -> int:
    if SYSTEM_BITS == 64:
        if _is_wow_64_process(handle):
            return 32

        return 64

    return 32


CAN_NOT_FIND_MODULE = "can not find module {}"


def get_base_address(process_id: int, module_name: str) -> int:
    modules = _iter_modules(process_id)
    lookup_name = module_name.casefold()

    for module in modules:
        if module.name.casefold() == lookup_name:
            modules.close()
            break

    else:
        raise LookupError(CAN_NOT_FIND_MODULE.format(tick(module_name)))

    return module.base_address


get_base_address_from_handle = unimplemented


CAN_NOT_FIND_PROCESS = "can not find process {}"


def get_process_id_from_name(name: str) -> int:
    processes = _iter_processes()
    lookup_name = name.casefold()

    for process in processes:
        if process.name.casefold() == lookup_name:
            processes.close()
            break

    else:
        raise LookupError(CAN_NOT_FIND_PROCESS.format(tick(name)))

    return process.process_id


def get_process_id_from_title(title: str) -> int:
    window = _find_window(None, ctypes.c_char_p(title.encode(DEFAULT_ENCODING, DEFAULT_ERRORS)))

    process_id = wintypes.DWORD(0)

    _get_window_process_id(window, ctypes.byref(process_id))

    return process_id.value


def open(process_id: int) -> int:
    return _open_process(PROCESS_ALL_ACCESS, False, process_id)


def close(handle: int) -> None:
    _close_handle(handle)


def allocate(
    handle: int,
    address: int,
    size: int,
    permissions: Permissions = Permissions.DEFAULT,
) -> int:
    return _virtual_alloc(
        handle, address, size, MEMORY_RESERVE | MEMORY_COMMIT, PERMISSIONS[permissions]
    )


def free(handle: int, address: int, size: int) -> None:
    _virtual_free(handle, address, size, MEMORY_RELEASE)


def terminate(handle: int) -> bool:
    return bool(_terminate_process(handle, 0))


def protect(
    handle: int,
    address: int,
    size: int,
    permissions: Permissions = Permissions.DEFAULT,
) -> int:
    old_protect = wintypes.DWORD(0)

    _virtual_protect(handle, address, size, PERMISSIONS[permissions], ctypes.byref(old_protect))

    return old_protect.value


def read(handle: int, address: int, size: int) -> bytes:
    buffer = ctypes.create_string_buffer(size)

    bytes_read = ctypes.c_size_t(0)

    _read_process_memory(handle, address, buffer, size, ctypes.byref(bytes_read))

    return buffer.raw


def write(handle: int, address: int, data: bytes) -> None:
    size = len(data)

    buffer = ctypes.create_string_buffer(data, size)

    bytes_written = ctypes.c_size_t(0)

    _write_process_memory(handle, address, buffer, size, ctypes.byref(bytes_written))
