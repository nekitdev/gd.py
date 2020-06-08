from ctypes import wintypes
import ctypes

from gd.memory.utils import Structure, func_def

kernel32 = ctypes.WinDLL("kernel32.dll")
user32 = ctypes.WinDLL("user32.dll")

SNAPPROCESS = 0x02
SNAPMODULE = 0x08
SNAPMODULE32 = 0x10
PROCESS_ALL_ACCESS = 0x100000 | 0x0F0000 | 0x000FFF
MAX_MODULE_NAME32 = 0x100  # 0xff + 1
PAGE_EXECUTE_READWRITE = 0x40

JMP = bytes([0xE9])


class ProcessEntry32(Structure):
    dwSize: wintypes.DWORD
    cntUsage: wintypes.DWORD
    th32ProcessID: wintypes.DWORD
    th32DefaultHeapID: ctypes.POINTER(ctypes.c_ulong)
    th32ModuleID: wintypes.DWORD
    cntThreads: wintypes.DWORD
    th32ParentProcessID: wintypes.DWORD
    pcPriClassBase: wintypes.LONG
    dwFlags: wintypes.DWORD
    szExeFile: ctypes.c_char * wintypes.MAX_PATH

    @property
    def name(self) -> str:
        return self.szExeFile.decode("utf-8")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.dwSize = ctypes.sizeof(self)


class ModuleEntry32(Structure):
    dwSize: wintypes.DWORD
    th32ModuleID: wintypes.DWORD
    th32ProcessID: wintypes.DWORD
    GlblcntUsage: wintypes.DWORD
    ProccntUsage: wintypes.DWORD
    modBaseAddr: ctypes.POINTER(wintypes.BYTE)
    modBaseSize: wintypes.DWORD
    hModule: wintypes.HMODULE
    szModule: ctypes.c_char * MAX_MODULE_NAME32
    szExePath: ctypes.c_char * wintypes.MAX_PATH

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.dwSize = ctypes.sizeof(self)

    @property
    def base_address(self):
        return ctypes.addressof(self.modBaseAddr.contents)

    @property
    def name(self):
        return self.szModule.decode("utf-8")


LPPROCESSENTRY32 = ctypes.POINTER(ProcessEntry32)
LPMODULEENTRY32 = ctypes.POINTER(ModuleEntry32)


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
    address: wintypes.DWORD, inherit_handle: wintypes.BOOL, process_id: wintypes.DWORD
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


@func_def(user32.FindWindowA)
def find_window(class_name: wintypes.LPCSTR, title: wintypes.LPCSTR) -> wintypes.HWND:
    pass


@func_def(user32.GetWindowThreadProcessId)
def get_window_thread_process_id(
    handle: wintypes.HWND, process_id_ptr: wintypes.LPDWORD
) -> wintypes.DWORD:
    pass


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

    process = process_first(process_snap, ctypes.byref(process_entry))

    while process:
        if process_entry.name == process_name:
            pid = process_entry.th32ProcessID
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

    module = module_first(module_snap, ctypes.byref(module_entry))

    while module:
        if module_entry.name == module_name:
            address = module_entry.base_address
            close_handle(module_snap)
            return address

        module = module_next(module_snap, ctypes.byref(module_entry))

    else:
        close_handle(module_snap)
        raise RuntimeError(f"{module_name!r} was not found. Error: {kernel32.GetLastError()}.")
