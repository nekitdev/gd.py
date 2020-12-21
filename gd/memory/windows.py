# type: ignore

import ctypes
import types
from pathlib import Path

import pefile  # to parse some headers uwu ~ nekit

from gd.enums import Protection
from gd.memory.utils import Structure, extern_fn
from gd.platform import system_bits
from gd.typing import Dict, Iterator, Optional, Type, Union

__all__ = (
    "allocate_memory",
    "free_memory",
    "get_base_address",
    "get_base_address_from_handle",
    "get_process_bits",
    "get_process_bits_from_handle",
    "open_process",
    "close_process",
    "get_process_id_from_name",
    "get_process_id_from_window_title",
    "get_process_name_from_id",
    "inject_dll",
    "terminate_process",
    "protect_process_memory",
    "read_process_memory",
    "write_process_memory",
)

try:
    from ctypes import wintypes

except ValueError:  # variant ... is not supported
    raise ImportError("Can not define memory functions for Windows.") from None

try:
    ctypes.WinDLL  # type: ignore

except AttributeError:
    raise ImportError("Can not define memory functions for Windows.") from None

try:
    kernel32 = ctypes.WinDLL("kernel32.dll")  # type: ignore
    user32 = ctypes.WinDLL("user32.dll")  # type: ignore

except OSError:
    raise ImportError("Can not define memory functions for Windows.") from None

ENCODING = "utf-8"

INFINITE = 0xFFFFFFFF

MAX_MODULE_NAME32 = 0xFF

MEM_RESERVE = 0x1000
MEM_COMMIT = 0x2000
MEM_RELEASE = 0x8000

PAGE_NOACCESS = 0x01
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04

PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40

NONE = Protection.NONE
READ = Protection.READ
WRITE = Protection.WRITE
EXECUTE = Protection.EXECUTE

PROTECTION_FLAGS = {
    NONE: PAGE_NOACCESS,
    READ: PAGE_READONLY,
    WRITE: PAGE_READWRITE,
    EXECUTE: PAGE_EXECUTE,
    READ | WRITE: PAGE_READWRITE,
    READ | EXECUTE: PAGE_EXECUTE_READ,
    WRITE | EXECUTE: PAGE_EXECUTE_READWRITE,
    READ | WRITE | EXECUTE: PAGE_EXECUTE_READWRITE,
}

PROCESS_ALL_ACCESS = 0x100000 | 0x0F0000 | 0x000FFF

SNAPPROCESS = 0x02

SNAPMODULE = 0x08
SNAPMODULE32 = 0x10


class ProcessEntry32(Structure):
    size: wintypes.DWORD
    count_usage: wintypes.DWORD
    process_id: wintypes.DWORD
    default_heap_id: ctypes.POINTER(wintypes.ULONG)
    module_id: wintypes.DWORD
    count_threads: wintypes.DWORD
    parent_process_id: wintypes.DWORD
    base_priority: wintypes.LONG
    flags: wintypes.DWORD
    exe_file: wintypes.CHAR * wintypes.MAX_PATH

    @property
    def id(self) -> int:
        return self.process_id

    @property
    def name(self) -> str:
        return self.exe_file.decode(ENCODING)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.size = ctypes.sizeof(self)


LPPROCESSENTRY32 = ctypes.POINTER(ProcessEntry32)


class ModuleEntry32(Structure):
    size: wintypes.DWORD
    module_id: wintypes.DWORD
    process_id: wintypes.DWORD
    global_count_usage: wintypes.DWORD
    proc_count_usage: wintypes.DWORD
    module_base_address: ctypes.POINTER(wintypes.BYTE)
    module_base_size: wintypes.DWORD
    module_handle: wintypes.HMODULE
    module_name: wintypes.CHAR * (MAX_MODULE_NAME32 + 1)
    exe_path: wintypes.CHAR * wintypes.MAX_PATH

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.size = ctypes.sizeof(self)

    @property
    def base_address(self) -> int:
        return ctypes.addressof(self.module_base_address.contents)

    @property
    def name(self) -> str:
        return self.module_name.decode(ENCODING)

    @property
    def path(self) -> str:
        return self.exe_path.decode(ENCODING)


LPMODULEENTRY32 = ctypes.POINTER(ModuleEntry32)


class SecurityAttributes(Structure):
    length: wintypes.DWORD
    security_descriptor: wintypes.LPVOID
    inherit_handle: wintypes.BOOL

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.length = ctypes.sizeof(self)


LPSECURITY_ATTRIBUTES = ctypes.POINTER(SecurityAttributes)


@extern_fn(kernel32.CreateToolhelp32Snapshot)
def _create_snapshot(flags: wintypes.DWORD, process_id: wintypes.DWORD) -> wintypes.HANDLE:
    pass


@extern_fn(kernel32.Process32First)
def _process_first(handle: wintypes.HANDLE, entry_ptr: LPPROCESSENTRY32) -> wintypes.BOOL:
    pass


@extern_fn(kernel32.Process32Next)
def _process_next(handle: wintypes.HANDLE, entry_ptr: LPPROCESSENTRY32) -> wintypes.BOOL:
    pass


@extern_fn(kernel32.Module32First)
def _module_first(handle: wintypes.HANDLE, entry_ptr: LPMODULEENTRY32) -> wintypes.BOOL:
    pass


@extern_fn(kernel32.Module32Next)
def _module_next(handle: wintypes.HANDLE, entry_ptr: LPMODULEENTRY32) -> wintypes.BOOL:
    pass


@extern_fn(kernel32.CloseHandle)
def _close_handle(handle: wintypes.HANDLE) -> wintypes.BOOL:
    pass


@extern_fn(kernel32.OpenProcess)
def _open_process(
    access: wintypes.DWORD, inherit_handle: wintypes.BOOL, process_id: wintypes.DWORD
) -> wintypes.HANDLE:
    pass


@extern_fn(kernel32.ReadProcessMemory)
def _read_process_memory(
    handle: wintypes.HANDLE,
    base_address: wintypes.LPVOID,
    buffer: wintypes.LPCVOID,
    size: ctypes.c_size_t,
    size_ptr: ctypes.POINTER(ctypes.c_size_t),
) -> wintypes.BOOL:
    pass


@extern_fn(kernel32.WriteProcessMemory)
def _write_process_memory(
    handle: wintypes.HANDLE,
    base_address: wintypes.LPVOID,
    buffer: wintypes.LPCVOID,
    size: ctypes.c_size_t,
    size_ptr: ctypes.POINTER(ctypes.c_size_t),
) -> wintypes.BOOL:
    pass


@extern_fn(kernel32.VirtualAllocEx)
def _virtual_alloc(
    handle: wintypes.HANDLE,
    address: wintypes.LPVOID,
    size: ctypes.c_size_t,
    allocation_type: wintypes.DWORD,
    protect: wintypes.DWORD,
) -> wintypes.LPVOID:
    pass


@extern_fn(kernel32.VirtualFreeEx)
def _virtual_free(
    handle: wintypes.HANDLE,
    address: wintypes.LPVOID,
    size: ctypes.c_size_t,
    free_type: wintypes.DWORD,
) -> wintypes.BOOL:
    pass


@extern_fn(kernel32.WaitForSingleObject)
def _wait_for_single_object(
    handle: wintypes.HANDLE, time_milliseconds: wintypes.DWORD
) -> wintypes.DWORD:
    pass


@extern_fn(kernel32.TerminateProcess)
def _terminate_process(handle: wintypes.HANDLE, exit_code: wintypes.UINT) -> wintypes.BOOL:
    pass


@extern_fn(user32.FindWindowA)
def _find_window(class_name: wintypes.LPCSTR, title: wintypes.LPCSTR) -> wintypes.HWND:
    pass


@extern_fn(user32.GetWindowThreadProcessId)
def _get_window_process_id(
    handle: wintypes.HWND, process_id_ptr: wintypes.LPDWORD
) -> wintypes.DWORD:
    pass


@extern_fn(kernel32.IsWow64Process)
def _is_wow_64_process_via_ptr(handle: wintypes.HANDLE, bool_ptr: wintypes.PBOOL) -> wintypes.BOOL:
    pass


@extern_fn(kernel32.GetSystemWow64DirectoryA)
def _get_system_wow_64_directory(
    string_buffer: wintypes.LPSTR, size: wintypes.UINT
) -> wintypes.UINT:
    pass


@extern_fn(kernel32.CreateRemoteThread)
def _create_remote_thread(
    handle: wintypes.HANDLE,
    thread_attributes: LPSECURITY_ATTRIBUTES,
    stack_size: ctypes.c_size_t,
    start_address: wintypes.LPVOID,
    start_parameter: wintypes.LPVOID,
    flags: wintypes.DWORD,
    thread_id: wintypes.LPDWORD,
) -> wintypes.HANDLE:
    pass


@extern_fn(kernel32.GetModuleHandleA)
def _get_module_handle(module_name: wintypes.LPCSTR) -> wintypes.HMODULE:
    pass


@extern_fn(kernel32.GetProcAddress)
def _get_proc_address(
    module_handle: wintypes.HMODULE, proc_name: wintypes.LPCSTR
) -> wintypes.LPVOID:
    pass


@extern_fn(kernel32.VirtualProtectEx)
def _virtual_protect(
    handle: wintypes.HANDLE,
    address: wintypes.LPVOID,
    size: ctypes.c_size_t,
    flags: wintypes.DWORD,
    old_protect: wintypes.PDWORD,
) -> wintypes.BOOL:
    pass


def _get_module_symbols(module_path: Union[str, Path]) -> Dict[str, int]:
    module_path = Path(module_path)

    pe = pefile.PE(module_path, fast_load=True)
    pe.parse_data_directories([pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])

    return {
        symbol.name.decode("utf-8"): symbol.address for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols
    }


class _CloseHandleManager:
    def __init__(self, handle: wintypes.HANDLE) -> None:
        self._handle = handle

    def __enter__(self) -> wintypes.HANDLE:
        return self._handle

    def __exit__(
        self, error_type: Type[BaseException], error: BaseException, traceback: types.TracebackType
    ) -> None:
        _close_handle(self._handle)


def _close_handle_manager(handle: wintypes.HANDLE) -> _CloseHandleManager:
    return _CloseHandleManager(handle)


def _iter_processes() -> Iterator[ProcessEntry32]:
    process_snapshot = _create_snapshot(SNAPPROCESS, 0)

    process_entry = ProcessEntry32()

    process = _process_first(process_snapshot, ctypes.byref(process_entry))

    with _close_handle_manager(process_snapshot):
        while process:
            yield process_entry
            process = _process_next(process_snapshot, ctypes.byref(process_entry))


def _iter_modules(process_id: int) -> Iterator[ModuleEntry32]:
    module_snapshot = _create_snapshot(SNAPMODULE | SNAPMODULE32, process_id)

    module_entry = ModuleEntry32()

    module = _module_first(module_snapshot, ctypes.byref(module_entry))

    with _close_handle_manager(module_snapshot):
        while module:
            yield module_entry
            module = _module_next(module_snapshot, ctypes.byref(module_entry))


def _get_process_module_handle(process_id: int, name: str) -> int:
    modules = _iter_modules(process_id)
    lookup_name = name.casefold()

    for module in modules:
        if module.name.casefold() == lookup_name:
            modules.close()
            break

    else:
        raise LookupError(f"Can not find module: {name!r}.")

    return module.module_handle


def _is_wow_64_process(process_handle: wintypes.HANDLE) -> bool:
    result = wintypes.BOOL(0)

    _is_wow_64_process_via_ptr(process_handle, ctypes.byref(result))

    return bool(result.value)


def _get_system_wow_64_dir() -> Optional[Path]:
    size = _get_system_wow_64_directory(None, 0)

    if not size:
        return

    path_buffer = ctypes.create_string_buffer(size)

    _get_system_wow_64_directory(path_buffer, size)

    return Path(path_buffer.value.decode(ENCODING))


def _get_module_proc_address(module_name: str, proc_name: str) -> int:
    handle = _get_module_handle(ctypes.c_char_p(module_name.encode()))

    address = _get_proc_address(handle, ctypes.c_char_p(proc_name.encode()))

    return address


_kernel32_name = "kernel32.dll"
_load_library_name = "LoadLibraryA"

_system_wow_64_dir = _get_system_wow_64_dir()

if _system_wow_64_dir:
    _kernel32_symbols = _get_module_symbols(_system_wow_64_dir / _kernel32_name)
else:
    _kernel32_symbols = {}


def _inject_dll(process_id: int, path: Union[str, Path]) -> int:
    path = Path(path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Given DLL path does not exist: {path}.")

    process_handle = open_process(process_id)

    path_bytes = str(path).encode(ENCODING)
    path_size = len(path_bytes) + 1  # increment to account for null terminator

    # allocate memory required to put our DLL path
    parameter_address = allocate_memory(process_handle, 0, path_size)

    # write DLL path string into allocated space
    write_process_memory(process_handle, parameter_address, path_bytes)

    if _is_wow_64_process(process_handle):  # if we are injecting into 32-bit process from 64-bit
        # get base address to kernel32.dll module of the process
        module_base = get_base_address(process_id, _kernel32_name)
        # look up offset of LoadLibraryA in PE header of WoW64 kernel32.dll
        load_library_offset = _kernel32_symbols.get(_load_library_name, 0)
        # if function is not present, raise an error
        if not load_library_offset:
            raise LookupError(f"Can not find {_load_library_name} in WoW64 kernel32.dll module.")
        # otherwise, get an actual address
        load_library = module_base + load_library_offset

    else:  # otherwise, get address normally
        load_library = _get_module_proc_address("kernel32.dll", "LoadLibraryA")

    thread_id = wintypes.DWORD(0)

    # create remote thread, with start routine of LoadLibraryA(DLLPath)
    thread_handle = _create_remote_thread(
        process_handle, None, 0, load_library, parameter_address, 0, ctypes.byref(thread_id)
    )

    # wait for the handle
    _wait_for_single_object(thread_handle, INFINITE)

    # free memory used to allocate DLL path
    free_memory(process_handle, parameter_address, path_size)

    # close process and thread handles
    _close_handle(process_handle)
    _close_handle(thread_handle)

    return thread_id.value


def get_process_bits(process_id: int) -> int:
    return get_process_bits_from_handle(open_process(process_id))


def get_process_bits_from_handle(process_handle: int) -> int:
    if system_bits >= 64:
        if _is_wow_64_process(process_handle):
            return 32

        return 64

    return 32


def get_base_address(process_id: int, module_name: str) -> int:
    modules = _iter_modules(process_id)
    lookup_name = module_name.casefold()

    for module in modules:
        if module.name.casefold() == lookup_name:
            modules.close()
            break

    else:
        raise LookupError(f"Can not find module: {module_name!r}.")

    return module.base_address


def get_base_address_from_handle(process_handle: int) -> int:
    raise NotImplementedError(
        "get_base_address_from_handle(process_handle) is not implemented on Windows."
    )


def get_process_name_from_id(process_id: int) -> str:
    processes = _iter_processes()

    for process in processes:
        if process.id == process_id:
            processes.close()
            break

    else:
        raise LookupError(f"Can not find process name with ID: {process_id!r}.")

    return process.name


def get_process_id_from_name(name: str) -> int:
    processes = _iter_processes()
    lookup_name = name.casefold()

    for process in processes:
        if process.name.casefold() == lookup_name:
            processes.close()
            break

    else:
        raise LookupError(f"Can not find process: {name!r}.")

    return process.process_id


def get_process_id_from_window_title(window_title: str) -> int:
    window = _find_window(None, ctypes.c_char_p(window_title.encode(ENCODING)))

    process_id = wintypes.DWORD(0)

    _get_window_process_id(window, ctypes.byref(process_id))

    return process_id.value


def open_process(process_id: int) -> int:
    return _open_process(PROCESS_ALL_ACCESS, False, process_id)


def close_process(process_handle: int) -> None:
    _close_handle(process_handle)


def allocate_memory(
    process_handle: int, address: int, size: int, flags: Protection = READ | WRITE | EXECUTE,
) -> int:
    return _virtual_alloc(
        process_handle, address, size, MEM_RESERVE | MEM_COMMIT, PROTECTION_FLAGS[flags]
    )


def free_memory(process_handle: int, address: int, size: int) -> None:
    _virtual_free(process_handle, address, size, MEM_RELEASE)


def terminate_process(process_handle: int) -> bool:
    return bool(_terminate_process(process_handle, 0))


def protect_process_memory(
    process_handle: int, address: int, size: int, flags: Protection = READ | WRITE | EXECUTE,
) -> int:
    old_protect = wintypes.DWORD(0)

    _virtual_protect(
        process_handle, address, size, PROTECTION_FLAGS[flags], ctypes.byref(old_protect)
    )

    return old_protect.value


def read_process_memory(process_handle: int, address: int, size: int) -> bytes:
    buffer = ctypes.create_string_buffer(size)

    bytes_read = ctypes.c_size_t(0)

    _read_process_memory(process_handle, address, buffer, size, ctypes.byref(bytes_read))

    return buffer.raw


def write_process_memory(process_handle: int, address: int, data: bytes) -> int:
    size = len(data)

    buffer = ctypes.create_string_buffer(data, size)

    bytes_written = ctypes.c_size_t(0)

    _write_process_memory(process_handle, address, buffer, size, ctypes.byref(bytes_written))

    return bytes_written.value


def inject_dll(process_id: int, path: Union[str, Path]) -> bool:
    return bool(_inject_dll(process_id, path))
