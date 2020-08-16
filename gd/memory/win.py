from ctypes import wintypes
import ctypes
from pathlib import Path

import pefile  # to parse some headers uwu ~ nekit

from gd.typing import Dict, Optional, Union
from gd.memory.utils import Structure, func_def

kernel32 = ctypes.WinDLL("kernel32.dll")
user32 = ctypes.WinDLL("user32.dll")

SNAPPROCESS = 0x02
SNAPMODULE = 0x08
SNAPMODULE32 = 0x10
PROCESS_ALL_ACCESS = 0x100000 | 0x0F0000 | 0x000FFF
MEM_RESERVE = 0x1000
MEM_COMMIT = 0x2000
MEM_RELEASE = 0x8000
INFINITE = 0xFFFFFFFF
MAX_MODULE_NAME32 = 0x100  # 0xff + 1
PAGE_READWRITE = 0x04
PAGE_EXECUTE_READWRITE = 0x40

JMP = bytes([0xE9])


class ProcessEntry32(Structure):
    size: wintypes.DWORD
    count_usage: wintypes.DWORD
    process_id: wintypes.DWORD
    default_heap_id: ctypes.POINTER(ctypes.c_ulong)
    module_id: wintypes.DWORD
    count_threads: wintypes.DWORD
    parent_process_id: wintypes.DWORD
    base_priority: wintypes.LONG
    flags: wintypes.DWORD
    exe_file: ctypes.c_char * wintypes.MAX_PATH

    @property
    def name(self) -> str:
        return self.exe_file.decode("utf-8")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.size = ctypes.sizeof(self)


class ModuleEntry32(Structure):
    size: wintypes.DWORD
    module_id: wintypes.DWORD
    process_id: wintypes.DWORD
    global_count_usage: wintypes.DWORD
    proc_count_usage: wintypes.DWORD
    module_base_address: ctypes.POINTER(wintypes.BYTE)
    module_base_size: wintypes.DWORD
    module_handle: wintypes.HMODULE
    module_name: ctypes.c_char * MAX_MODULE_NAME32
    exe_path: ctypes.c_char * wintypes.MAX_PATH

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.size = ctypes.sizeof(self)

    @property
    def base_address(self) -> int:
        return ctypes.addressof(self.module_base_address.contents)

    @property
    def name(self) -> str:
        return self.module_name.decode("utf-8")

    @property
    def path(self) -> str:
        return self.exe_path.decode("utf-8")


class SecurityAttributes(Structure):
    length: wintypes.DWORD
    security_descriptor: wintypes.LPVOID
    inherit_handle: wintypes.BOOL

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.length = ctypes.sizeof(self)


LPPROCESSENTRY32 = ctypes.POINTER(ProcessEntry32)
LPMODULEENTRY32 = ctypes.POINTER(ModuleEntry32)
LPSECURITY_ATTRIBUTES = ctypes.POINTER(SecurityAttributes)


@func_def(kernel32.CreateToolhelp32Snapshot)
def create_snapshot(flags: wintypes.DWORD, process_id: wintypes.DWORD) -> wintypes.HANDLE:
    pass


@func_def(kernel32.Process32First)
def process_first(handle: wintypes.HANDLE, entry_ptr: LPPROCESSENTRY32) -> wintypes.BOOL:
    pass


@func_def(kernel32.Process32Next)
def process_next(handle: wintypes.HANDLE, entry_ptr: LPPROCESSENTRY32) -> wintypes.BOOL:
    pass


@func_def(kernel32.CloseHandle)
def close_handle(handle: wintypes.HANDLE) -> wintypes.BOOL:
    pass


@func_def(kernel32.Module32First)
def module_first(handle: wintypes.HANDLE, entry_ptr: LPMODULEENTRY32) -> wintypes.BOOL:
    pass


@func_def(kernel32.Module32Next)
def module_next(handle: wintypes.HANDLE, entry_ptr: LPMODULEENTRY32) -> wintypes.BOOL:
    pass


@func_def(kernel32.ReadProcessMemory)
def read_process_memory(
    handle: wintypes.HANDLE,
    base_address: wintypes.LPVOID,
    buffer: wintypes.LPCVOID,
    size: ctypes.c_size_t,
    size_ptr: ctypes.POINTER(ctypes.c_size_t),
) -> wintypes.BOOL:
    pass


@func_def(kernel32.WriteProcessMemory)
def write_process_memory(
    handle: wintypes.HANDLE,
    base_address: wintypes.LPVOID,
    buffer: wintypes.LPCVOID,
    size: ctypes.c_size_t,
    size_ptr: ctypes.POINTER(ctypes.c_size_t),
) -> wintypes.BOOL:
    pass


@func_def(kernel32.OpenProcess)
def open_process(
    access: wintypes.DWORD, inherit_handle: wintypes.BOOL, process_id: wintypes.DWORD
) -> wintypes.HANDLE:
    pass


@func_def(kernel32.VirtualProtectEx)
def virtual_protect_ex(
    handle: wintypes.HANDLE,
    address: wintypes.LPVOID,
    size: ctypes.c_size_t,
    flags: wintypes.DWORD,
    old_protect: wintypes.PDWORD,
) -> wintypes.BOOL:
    pass


@func_def(kernel32.VirtualAllocEx)
def virtual_alloc_ex(
    handle: wintypes.HANDLE,
    address: wintypes.LPVOID,
    size: ctypes.c_size_t,
    allocation_type: wintypes.DWORD,
    protect: wintypes.DWORD,
) -> wintypes.LPVOID:
    pass


@func_def(kernel32.VirtualFreeEx)
def virtual_free_ex(
    handle: wintypes.HANDLE,
    address: wintypes.LPVOID,
    size: ctypes.c_size_t,
    free_type: wintypes.DWORD,
) -> wintypes.BOOL:
    pass


@func_def(kernel32.CreateRemoteThread)
def create_remote_thread(
    handle: wintypes.HANDLE,
    thread_attributes: LPSECURITY_ATTRIBUTES,
    stack_size: ctypes.c_size_t,
    start_address: wintypes.LPVOID,
    start_parameter: wintypes.LPVOID,
    flags: wintypes.DWORD,
    thread_id: wintypes.LPDWORD,
) -> wintypes.HANDLE:
    pass


@func_def(kernel32.GetModuleHandleA)
def get_module_handle(module_name: wintypes.LPCSTR) -> wintypes.HMODULE:
    pass


@func_def(kernel32.GetProcAddress)
def get_proc_address(
    module_handle: wintypes.HMODULE, proc_name: wintypes.LPCSTR
) -> wintypes.LPVOID:
    pass


@func_def(kernel32.WaitForSingleObject)
def wait_for_single_object(handle: wintypes.HANDLE, time_ms: wintypes.DWORD) -> wintypes.DWORD:
    pass


@func_def(kernel32.IsWow64Process)
def is_wow_64_process_impl(handle: wintypes.HANDLE, bool_ptr: wintypes.PBOOL) -> wintypes.BOOL:
    pass


@func_def(kernel32.GetSystemWow64DirectoryA)
def get_system_wow_64_dir_a(string_buffer: wintypes.LPSTR, size: wintypes.UINT) -> wintypes.UINT:
    pass


@func_def(kernel32.TerminateProcess)
def terminate_process(process_handle: wintypes.HANDLE, exit_code: ctypes.c_uint) -> wintypes.BOOL:
    pass


@func_def(user32.FindWindowA)
def find_window(class_name: wintypes.LPCSTR, title: wintypes.LPCSTR) -> wintypes.HWND:
    pass


@func_def(user32.GetWindowThreadProcessId)
def get_window_thread_process_id(
    handle: wintypes.HWND, process_id_ptr: wintypes.LPDWORD
) -> wintypes.DWORD:
    pass


def get_module_proc_address(module_name: str, proc_name: str, is_32_bit: bool = True) -> int:
    handle = get_module_handle(ctypes.c_char_p(module_name.encode()))

    address = get_proc_address(handle, ctypes.c_char_p(proc_name.encode()))

    return address if address else 0


def get_module_symbols(module_path: Union[str, Path]) -> Dict[str, int]:
    module_path = Path(module_path)

    pe = pefile.PE(module_path, fast_load=True)
    pe.parse_data_directories([pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])

    return {
        symbol.name.decode("utf-8"): symbol.address for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols
    }


def get_window_process_id(title: str) -> int:
    process_id = wintypes.DWORD(0)

    window = find_window(None, ctypes.c_char_p(title.encode()))
    get_window_thread_process_id(window, ctypes.byref(process_id))

    return process_id.value


def virtual_protect(handle: int, address: int, size: int, flags: int) -> int:
    old_protect = wintypes.DWORD(0)
    virtual_protect_ex(handle, ctypes.c_void_p(address), size, flags, ctypes.byref(old_protect))
    return old_protect.value


def get_pid_from_name(process_name: str) -> int:
    process_snap = create_snapshot(SNAPPROCESS, 0)
    process_entry = ProcessEntry32()
    process_name = process_name.casefold()

    process = process_first(process_snap, ctypes.byref(process_entry))

    while process:
        if process_entry.name.casefold() == process_name:
            pid = process_entry.process_id
            close_handle(process_snap)
            return pid

        process = process_next(process_snap, ctypes.byref(process_entry))

    else:
        close_handle(process_snap)
        raise RuntimeError(f"{process_name!r} was not found.")


def get_handle(pid: int) -> wintypes.HANDLE:
    return open_process(PROCESS_ALL_ACCESS, 0, pid)


def get_base_address(pid: int, module_name: str) -> int:
    module_snap = create_snapshot(SNAPMODULE | SNAPMODULE32, pid)
    module_entry = ModuleEntry32()
    module_name = module_name.casefold()

    module = module_first(module_snap, ctypes.byref(module_entry))

    while module:
        if module_entry.name.casefold() == module_name:
            address = module_entry.base_address
            close_handle(module_snap)
            return address

        module = module_next(module_snap, ctypes.byref(module_entry))

    else:
        close_handle(module_snap)
        raise RuntimeError(f"{module_name!r} was not found. Error: {kernel32.GetLastError()}.")


def get_system_wow_64_dir() -> Optional[Path]:
    size = get_system_wow_64_dir_a(None, 0)

    if not size:
        return

    string_buffer = ctypes.create_string_buffer(size)
    get_system_wow_64_dir_a(string_buffer, size)

    return Path(string_buffer.value.decode("utf-8"))


def allocate_memory(
    handle: int, size: int, address: int = 0, access: int = PAGE_EXECUTE_READWRITE
) -> int:
    return virtual_alloc_ex(handle, address, size, MEM_RESERVE | MEM_COMMIT, access)


def is_wow_64_process(process_handle: wintypes.HANDLE) -> bool:
    result = wintypes.BOOL(0)
    is_wow_64_process_impl(process_handle, ctypes.byref(result))
    return bool(result.value)


def inject_dll(process_id: int, dll_path: Union[str, Path]) -> int:
    dll_path = Path(dll_path).resolve()

    if not dll_path.exists():
        raise FileNotFoundError(f"Given DLL path does not exist: {dll_path}.")

    dll_path = str(dll_path)

    process = get_handle(process_id)  # get handle to our process

    data = ctypes.create_string_buffer(dll_path.encode())  # convert python str to cstr

    # allocate memory required to put our DLL path
    parameter_address = allocate_memory(process, len(data))

    # write DLL path string into allocated space
    write_process_memory(process, parameter_address, ctypes.byref(data), len(data), None)

    if is_wow_64_process(process):  # in case we are injecting into 32-bit process from 64-bit
        # get base address to kernel32.dll module of the process
        module_base = get_base_address(process_id, "kernel32.dll")
        # look up offset of LoadLibraryA in PE header of WoW64 kernel32.dll
        load_library = kernel32_symbols.get("LoadLibraryA", 0) + module_base
    else:  # otherwise, get address normally
        load_library = get_module_proc_address("kernel32.dll", "LoadLibraryA")

    thread_id = wintypes.DWORD(0)

    # create remote thread, with start routine of LoadLibraryA(DLLPath)
    handle = create_remote_thread(
        process, None, 0, load_library, parameter_address, 0, ctypes.byref(thread_id)
    )

    # wait for the handle
    wait_for_single_object(handle, INFINITE)

    # free memory used to allocate DLL path
    virtual_free_ex(process, parameter_address, 0, MEM_RELEASE)

    # close process and thread handles
    close_handle(process)
    close_handle(handle)

    return thread_id.value


system_wow_64_dir = get_system_wow_64_dir()

if system_wow_64_dir:
    kernel32_symbols = get_module_symbols(system_wow_64_dir / "kernel32.dll")
else:
    kernel32_symbols = {}
