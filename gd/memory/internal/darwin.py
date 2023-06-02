# type: ignore  # XXX: we need to be extremely careful here

import ctypes
from pathlib import Path
from typing import Iterator

from typing_extensions import TypeAlias

from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.enums import Permissions
from gd.memory.internal import unimplemented
from gd.memory.internal.utils import Struct, external
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

LIBC_DYLIB = "libc.dylib"

CAN_NOT_DEFINE_INTERNAL_FUNCTIONS_FOR_DARWIN = "can not define internal functions for darwin"

try:
    LIBC = ctypes.CDLL(LIBC_DYLIB)

except OSError:
    raise ImportError(CAN_NOT_DEFINE_INTERNAL_FUNCTIONS_FOR_DARWIN) from None


KERNEL_SUCCESS = 0

MAX_PATH_LENGTH = 1024

PROCESS_ALL_PIDS = 1
PROCESS_FLAG_LP64 = 0x10
PROCESS_PIDPATHINFO_MAXSIZE = MAX_PATH_LENGTH * 4
PROCESS_PIDT_SHORTBSDINFO = 13

MAX_SHORT_PROCESS_NAME_LENGTH = 16

VM_PROTECTION_NONE = 0x00
VM_PROTECTION_READ = 0x01
VM_PROTECTION_WRITE = 0x02
VM_PROTECTION_EXECUTE = 0x04

NONE = Permissions.NONE
READ = Permissions.READ
WRITE = Permissions.WRITE
EXECUTE = Permissions.EXECUTE

PERMISSIONS = {
    NONE: VM_PROTECTION_NONE,
    READ: VM_PROTECTION_READ,
    WRITE: VM_PROTECTION_WRITE,
    EXECUTE: VM_PROTECTION_EXECUTE,
    READ | WRITE: VM_PROTECTION_READ | VM_PROTECTION_WRITE,
    READ | EXECUTE: VM_PROTECTION_READ | VM_PROTECTION_EXECUTE,
    WRITE | EXECUTE: VM_PROTECTION_WRITE | VM_PROTECTION_EXECUTE,
    READ | WRITE | EXECUTE: VM_PROTECTION_READ | VM_PROTECTION_WRITE | VM_PROTECTION_EXECUTE,
}

bool_t = ctypes.c_uint

kernel_return_t = ctypes.c_int

mach_message_type_number_t = ctypes.c_uint

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
vm_protection_t = ctypes.c_int
vm_task_entry_t = mach_port_t

vm32_object_id_t = ctypes.c_uint32


class vm_region_submap_info_64(Struct):
    protection: vm_protection_t
    max_protection: vm_protection_t
    inheritance: vm_inherit_t
    offset: memory_object_offset_t
    user_tag: ctypes.c_uint
    pages_resident: ctypes.c_uint
    pages_shared_now_private: ctypes.c_uint
    pages_swapped_out: ctypes.c_uint
    pages_dirtied: ctypes.c_uint
    shadow_depth: ctypes.c_ushort
    is_submap: bool_t
    behavior: vm_behavior_t
    object_id: vm32_object_id_t
    used_wired_count: ctypes.c_ushort
    pages_reusable: ctypes.c_uint


CHAR_MAX_SHORT_PROCESS_NAME_LENGTH: TypeAlias = ctypes.c_char * MAX_SHORT_PROCESS_NAME_LENGTH


class proc_bsdshortinfo(Struct):
    process_id: ctypes.c_uint
    parent_process_id: ctypes.c_uint
    persistent_process_id: ctypes.c_uint
    status: ctypes.c_uint
    short_process_name: CHAR_MAX_SHORT_PROCESS_NAME_LENGTH
    flags: ctypes.c_uint
    user_id: ctypes.c_uint
    group_id: ctypes.c_uint
    real_user_id: ctypes.c_uint
    real_group_id: ctypes.c_uint
    serial_version_user_id: ctypes.c_uint
    serial_version_group_id: ctypes.c_uint
    reserved_for_future_use: ctypes.c_uint


@external(LIBC.proc_listpids)
def _process_listpids(
    type: ctypes.c_uint, type_info: ctypes.c_uint, buffer: ctypes.c_void_p, size: ctypes.c_uint
) -> ctypes.c_int:
    ...


@external(LIBC.proc_pidinfo)
def _process_pidinfo(
    process_id: ctypes.c_int,
    type: ctypes.c_int,
    argument: ctypes.c_uint64,
    buffer: ctypes.c_void_p,
    size: ctypes.c_uint,
) -> ctypes.c_int:
    ...


@external(LIBC.mach_task_self)
def _mach_task_self() -> mach_port_t:
    ...


@external(LIBC.task_terminate)
def _task_terminate(task: mach_port_t) -> kernel_return_t:
    ...


mach_port_t_pointer: TypeAlias = ctypes.POINTER(mach_port_t)


@external(LIBC.task_for_pid)
def _task_for_pid(
    port: mach_port_t, process_id: pid_t, target_port: mach_port_t_pointer
) -> kernel_return_t:
    ...


mach_vm_address_t_pointer: TypeAlias = ctypes.POINTER(mach_vm_address_t)
mach_vm_size_t_pointer: TypeAlias = ctypes.POINTER(mach_vm_size_t)
natural_t_pointer: TypeAlias = ctypes.POINTER(natural_t)
mach_message_type_number_t_pointer: TypeAlias = ctypes.POINTER(mach_message_type_number_t)


@external(LIBC.mach_vm_region_recurse)
def _mach_vm_region_recurse(
    task: vm_map_read_t,
    address: mach_vm_address_t_pointer,
    size: mach_vm_size_t_pointer,
    nesting_depth: natural_t_pointer,
    info: ctypes.c_void_p,  # vm_region_submap_info_64_t: can not cast to real type
    count: mach_message_type_number_t_pointer,
) -> kernel_return_t:
    ...


@external(LIBC.mach_vm_protect)
def _mach_vm_protect(
    task: vm_task_entry_t,
    address: mach_vm_address_t,
    size: mach_vm_size_t,
    set_maximum: bool_t,
    new_protection: vm_protection_t,
) -> kernel_return_t:
    ...


@external(LIBC.mach_vm_read_overwrite)
def _mach_vm_read_overwrite(
    task: vm_map_read_t,
    address: mach_vm_address_t,
    size: mach_vm_size_t,
    data: ctypes.c_void_p,  # mach_vm_address_t: can not cast to real type
    size_pointer: mach_vm_size_t_pointer,
) -> kernel_return_t:
    ...


@external(LIBC.mach_vm_write)
def _mach_vm_write(
    task: vm_map_t,
    address: mach_vm_address_t,
    data: ctypes.c_void_p,
    count: mach_message_type_number_t,
) -> kernel_return_t:
    ...


@external(LIBC.mach_vm_allocate)
def _mach_vm_allocate(
    task: vm_map_t,
    address: mach_vm_address_t_pointer,
    size: mach_vm_size_t,
    flags: ctypes.c_int,
) -> kernel_return_t:
    ...


@external(LIBC.mach_vm_deallocate)
def _mach_vm_deallocate(
    task: vm_map_t,
    address: mach_vm_address_t,
    size: mach_vm_size_t,
) -> kernel_return_t:
    ...


def _process_id_iterator() -> Iterator[int]:
    process_count = _process_listpids(PROCESS_ALL_PIDS, 0, None, 0)

    process_id_array = (pid_t * process_count)()

    _process_listpids(
        PROCESS_ALL_PIDS, 0, ctypes.byref(process_id_array), ctypes.sizeof(process_id_array)
    )

    for process_id in process_id_array:
        if process_id:
            yield process_id


def allocate(
    handle: int,
    address: int,  # ignored, as such functionality is not provided
    size: int,
    permissions: Permissions = Permissions.DEFAULT,
) -> int:
    actual_address = mach_vm_address_t(0)

    _mach_vm_allocate(handle, ctypes.byref(actual_address), size, PERMISSIONS[permissions])

    return actual_address.value


def free(handle: int, address: int, size: int) -> None:
    _mach_vm_deallocate(handle, address, size)


def get_base_address(process_id: int, module_name: str) -> int:
    return get_base_address_from_handle(open(process_id))


def get_base_address_from_handle(handle: int) -> int:
    base_address = mach_vm_address_t(0)
    size = mach_vm_size_t(0)
    nesting_depth = natural_t(0)
    info = vm_region_submap_info_64()
    count = mach_message_type_number_t(16)

    _mach_vm_region_recurse(
        handle,
        ctypes.byref(base_address),
        ctypes.byref(size),
        ctypes.byref(nesting_depth),
        ctypes.byref(info),
        ctypes.byref(count),
    )

    return base_address.value


def open(process_id: int) -> int:
    handle = mach_port_t(0)

    _task_for_pid(_mach_task_self(), process_id, handle)

    return handle.value


def close(handle: int) -> None:
    pass  # do nothing, as no shutdown is required


CAN_NOT_FIND_PROCESS = "can not find process {}"


def get_process_id_from_name(
    name: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> int:
    lookup_name = name.casefold()

    path_size = PROCESS_PIDPATHINFO_MAXSIZE
    path_buffer = ctypes.create_string_buffer(path_size)

    for process_id in _process_id_iterator():
        ctypes.memset(path_buffer, 0, path_size)  # re-use the buffer instead of creating a new one

        _process_listpids(process_id, path_buffer, path_size)

        path_value = path_buffer.value

        if path_value:
            path = Path(path_value.decode(DEFAULT_ENCODING, DEFAULT_ERRORS))

            if path.name.casefold() == lookup_name:
                return process_id

    else:
        raise LookupError(CAN_NOT_FIND_PROCESS.format(tick(name)))


def get_process_bits(process_id: int) -> int:
    process_info = proc_bsdshortinfo()

    _process_pidinfo(
        process_id,
        PROCESS_PIDT_SHORTBSDINFO,
        0,
        ctypes.byref(process_info),
        ctypes.sizeof(process_info),
    )

    if process_info.flags & PROCESS_FLAG_LP64:
        return 64

    return 32


get_process_bits_from_handle = unimplemented

get_process_id_from_title = unimplemented


def terminate(handle: int) -> bool:
    return not _task_terminate(handle)


def protect(
    handle: int,
    address: int,
    size: int,
    permissions: Permissions = Permissions.DEFAULT,
) -> int:
    _mach_vm_protect(handle, address, size, 0, PERMISSIONS[permissions])

    return 0


def read(handle: int, address: int, size: int) -> bytes:
    buffer = ctypes.create_string_buffer(size)

    bytes_read = mach_vm_size_t(0)

    _mach_vm_read_overwrite(handle, address, size, ctypes.byref(buffer), ctypes.byref(bytes_read))

    return buffer.raw


def write(handle: int, address: int, data: bytes) -> None:
    size = len(data)

    buffer = ctypes.create_string_buffer(data, size)

    _mach_vm_write(handle, address, ctypes.byref(buffer), size)
