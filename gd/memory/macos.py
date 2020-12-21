# type: ignore

import ctypes
import ctypes.util
from pathlib import Path

from gd.enums import Protection
from gd.memory.utils import Structure, extern_fn
from gd.typing import Iterator, Union

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
    libc = ctypes.CDLL("libc.dylib")  # type: ignore

except OSError:
    raise ImportError("Can not define memory functions for MacOS.") from None

ENCODING = "utf-8"

KERN_SUCCESS = 0

MAX_PATH_LEN = 1024

PROC_ALL_PIDS = 1
PROC_FLAG_LP64 = 0x10
PROC_PIDPATHINFO_MAXSIZE = MAX_PATH_LEN * 4
PROC_PIDT_SHORTBSDINFO = 13

MAX_SHORT_PROCESS_NAME_LENGTH = 16

VM_PROT_NONE = 0x00
VM_PROT_READ = 0x01
VM_PROT_WRITE = 0x02
VM_PROT_EXECUTE = 0x04

NONE = Protection.NONE
READ = Protection.READ
WRITE = Protection.WRITE
EXECUTE = Protection.EXECUTE

PROTECTION_FLAGS = {
    NONE: VM_PROT_NONE,
    READ: VM_PROT_READ,
    WRITE: VM_PROT_WRITE,
    EXECUTE: VM_PROT_EXECUTE,
    READ | WRITE: VM_PROT_READ | VM_PROT_WRITE,
    READ | EXECUTE: VM_PROT_READ | VM_PROT_EXECUTE,
    WRITE | EXECUTE: VM_PROT_WRITE | VM_PROT_EXECUTE,
    READ | WRITE | EXECUTE: VM_PROT_READ | VM_PROT_WRITE | VM_PROT_EXECUTE,
}

boolean_t = ctypes.c_uint

kern_return_t = ctypes.c_int

mach_msg_type_number_t = ctypes.c_uint

mach_port_t = ctypes.c_uint

mach_vm_address_t = ctypes.c_uint64
mach_vm_size_t = ctypes.c_uint64

memory_object_offset_t = ctypes.c_ulonglong

natural_t = ctypes.c_uint

pid_t = ctypes.c_int

c_uintptr_t = ctypes.c_ulong

vm_behavior_t = ctypes.c_int
vm_inherit_t = ctypes.c_uint
vm_map_t = mach_port_t
vm_map_read_t = mach_port_t
vm_offset_t = c_uintptr_t
vm_prot_t = ctypes.c_int
vm_task_entry_t = mach_port_t

vm32_object_id_t = ctypes.c_uint32


class vm_region_submap_info_64(Structure):
    protection: vm_prot_t
    max_protection: vm_prot_t
    inheritance: vm_inherit_t
    offset: memory_object_offset_t
    user_tag: ctypes.c_uint
    pages_resident: ctypes.c_uint
    pages_shared_now_private: ctypes.c_uint
    pages_swapped_out: ctypes.c_uint
    pages_dirtied: ctypes.c_uint
    shadow_depth: ctypes.c_ushort
    is_submap: boolean_t
    behavior: vm_behavior_t
    object_id: vm32_object_id_t
    used_wired_count: ctypes.c_ushort
    pages_reusable: ctypes.c_uint


class proc_bsdshortinfo(Structure):
    process_id: ctypes.c_uint
    parent_process_id: ctypes.c_uint
    persistent_process_id: ctypes.c_uint
    status: ctypes.c_uint
    short_process_name: ctypes.c_char * MAX_SHORT_PROCESS_NAME_LENGTH
    flags: ctypes.c_uint
    user_id: ctypes.c_uint
    group_id: ctypes.c_uint
    real_user_id: ctypes.c_uint
    real_group_id: ctypes.c_uint
    serial_version_user_id: ctypes.c_uint
    serial_version_group_id: ctypes.c_uint
    reserved_for_future_use: ctypes.c_uint


@extern_fn(libc.proc_listpids)
def _proc_listpids(
    type: ctypes.c_uint, type_info: ctypes.c_uint, buffer: ctypes.c_void_p, size: ctypes.c_uint
) -> ctypes.c_int:
    pass


@extern_fn(libc.proc_pidpath)
def _proc_pidpath(
    process_id: ctypes.c_int, path_buffer: ctypes.c_void_p, size: ctypes.c_uint
) -> ctypes.c_int:
    pass


@extern_fn(libc.proc_pidinfo)
def _proc_pidinfo(
    process_id: ctypes.c_int,
    type: ctypes.c_int,
    argument: ctypes.c_uint64,
    buffer: ctypes.c_void_p,
    size: ctypes.c_uint,
) -> ctypes.c_int:
    pass


@extern_fn(libc.mach_task_self)
def _mach_task_self() -> mach_port_t:
    pass


@extern_fn(libc.task_terminate)
def _task_terminate(task: mach_port_t) -> kern_return_t:
    pass


@extern_fn(libc.task_for_pid)
def _task_for_pid(
    port: mach_port_t, process_id: pid_t, target_port: ctypes.POINTER(mach_port_t)
) -> kern_return_t:
    pass


@extern_fn(libc.mach_vm_region_recurse)
def _mach_vm_region_recurse(
    task: vm_map_read_t,
    address: ctypes.POINTER(mach_vm_address_t),
    size: ctypes.POINTER(mach_vm_size_t),
    nesting_depth: ctypes.POINTER(natural_t),
    info: ctypes.c_void_p,  # vm_region_submap_info_64_t: can not cast to real type
    count: ctypes.POINTER(mach_msg_type_number_t),
) -> kern_return_t:
    pass


@extern_fn(libc.mach_vm_protect)
def _mach_vm_protect(
    task: vm_task_entry_t,
    address: mach_vm_address_t,
    size: mach_vm_size_t,
    set_maximum: boolean_t,
    new_protection: vm_prot_t,
) -> kern_return_t:
    pass


@extern_fn(libc.mach_vm_read_overwrite)
def _mach_vm_read_overwrite(
    task: vm_map_read_t,
    address: mach_vm_address_t,
    size: mach_vm_size_t,
    data: ctypes.c_void_p,  # mach_vm_address_t: can not cast to real type
    size_ptr: ctypes.POINTER(mach_vm_size_t),
) -> kern_return_t:
    pass


@extern_fn(libc.mach_vm_write)
def _mach_vm_write(
    task: vm_map_t,
    address: mach_vm_address_t,
    data: ctypes.c_void_p,
    count: mach_msg_type_number_t,
) -> kern_return_t:
    pass


@extern_fn(libc.mach_vm_allocate)
def _mach_vm_allocate(
    task: vm_map_t,
    address: ctypes.POINTER(mach_vm_address_t),
    size: mach_vm_size_t,
    flags: ctypes.c_int,
) -> kern_return_t:
    pass


@extern_fn(libc.mach_vm_deallocate)
def _mach_vm_deallocate(
    task: vm_map_t, address: mach_vm_address_t, size: mach_vm_size_t,
) -> kern_return_t:
    pass


def _process_id_iter() -> Iterator[int]:
    process_count = _proc_listpids(PROC_ALL_PIDS, 0, None, 0)

    process_id_array = (pid_t * process_count)()

    _proc_listpids(
        PROC_ALL_PIDS, 0, ctypes.byref(process_id_array), ctypes.sizeof(process_id_array)
    )

    for process_id in process_id_array:
        if process_id:
            yield process_id


def allocate_memory(
    process_handle: int,
    address: int,  # ignored, as such functionality is not provided
    size: int,
    flags: Protection = READ | WRITE | EXECUTE,
) -> int:
    actual_address = mach_vm_address_t(0)

    _mach_vm_allocate(process_handle, ctypes.byref(actual_address), size, PROTECTION_FLAGS[flags])

    return actual_address.value


def free_memory(process_handle: int, address: int, size: int) -> None:
    _mach_vm_deallocate(process_handle, address, size)


def get_base_address(process_id: int, module_name: str) -> int:
    return get_base_address_from_handle(open_process(process_id))


def get_base_address_from_handle(process_handle: int) -> int:
    base_address = mach_vm_address_t(0)
    size = mach_vm_size_t(0)
    nesting_depth = natural_t(0)
    info = vm_region_submap_info_64()
    count = mach_msg_type_number_t(16)

    _mach_vm_region_recurse(
        process_handle,
        ctypes.byref(base_address),
        ctypes.byref(size),
        ctypes.byref(nesting_depth),
        ctypes.byref(info),
        ctypes.byref(count),
    )

    return base_address.value


def open_process(process_id: int) -> int:
    process_handle = mach_port_t(0)

    _task_for_pid(_mach_task_self(), process_id, process_handle)

    return process_handle.value


def close_process(process_handle: int) -> None:
    pass  # do nothing, as no shutdown is required


def get_process_id_from_name(process_name: str) -> int:
    lookup_name = process_name.casefold()

    path_size = PROC_PIDPATHINFO_MAXSIZE
    path_buffer = ctypes.create_string_buffer(path_size)

    for process_id in _process_id_iter():
        ctypes.memset(path_buffer, 0, path_size)  # re-use the buffer instead of creating a new one

        _proc_pidpath(process_id, path_buffer, path_size)

        path_value = path_buffer.value

        if path_value:
            path = Path(path_value.decode(ENCODING))

            if path.name.casefold() == lookup_name:
                return process_id

    else:
        raise LookupError(f"Can not find process: {process_name!r}.")


def get_process_name_from_id(process_id: int) -> str:
    path_size = PROC_PIDPATHINFO_MAXSIZE
    path_buffer = ctypes.create_string_buffer(path_size)

    _proc_pidpath(process_id, path_buffer, path_size)

    path_value = path_buffer.value

    if path_value:
        path = Path(path_value.decode(ENCODING))

        return path.name

    raise LookupError(f"Can not find process name from ID: {process_id!r}.")


def get_process_bits(process_id: int) -> int:
    process_info = proc_bsdshortinfo()

    _proc_pidinfo(
        process_id,
        PROC_PIDT_SHORTBSDINFO,
        0,
        ctypes.byref(process_info),
        ctypes.sizeof(process_info),
    )

    if process_info.flags & PROC_FLAG_LP64:
        return 64

    return 32


def get_process_bits_from_handle(process_handle: int) -> int:
    raise NotImplementedError(
        "get_process_bits_from_handle(process_handle) is not yet implemented for MacOS."
    )


def get_process_id_from_window_title(window_title: str) -> int:
    raise NotImplementedError(
        "get_process_id_from_window_title(window_title) is not yet implemented for MacOS."
    )


def inject_dll(process_id: int, path: Union[str, Path]) -> bool:
    raise NotImplementedError("inject_dll(process_id, path) is not yet implemented for MacOS.")


def terminate_process(process_handle: int) -> bool:
    return not _task_terminate(process_handle)


def protect_process_memory(
    process_handle: int, address: int, size: int, flags: Protection = READ | WRITE | EXECUTE
) -> int:
    _mach_vm_protect(process_handle, address, size, 0, PROTECTION_FLAGS[flags])

    return 0


def read_process_memory(process_handle: int, address: int, size: int) -> bytes:
    buffer = ctypes.create_string_buffer(size)

    bytes_read = mach_vm_size_t(0)

    _mach_vm_read_overwrite(
        process_handle, address, size, ctypes.byref(buffer), ctypes.byref(bytes_read)
    )

    return buffer.raw


def write_process_memory(process_handle: int, address: int, data: bytes) -> int:
    size = len(data)

    buffer = ctypes.create_string_buffer(data, size)

    _mach_vm_write(process_handle, address, ctypes.byref(buffer), size)

    return size  # we can not check this
