"""Internal memory interfaces for different platforms.

Every module should define several functions and constants.

Functions
---------
:func:`allocate_memory` is used for allocating memory::

    def allocate_memory(process_handle: int, address: int, size: int, flags: gd.Protection) -> int:
        # allocate "size" bytes with "flags" permissions,
        # trying to start at "address", then return address to memory
        # note: "flags" should default to RWX (read, write, execute) permissions
        ...


:func:`free_memory` is used for freeing memory::

    def free_memory(process_handle: int, address: int, size: int) -> None:
        ...  # free "size" bytes, starting at "address"


:func:`get_base_address` is used for fetching base address of some module::

    # "process_id" and "module_name" as a workaround for windows
    # getting process handle and fetching using that may be needed
    def get_base_address(process_id: int, module_name: str) -> int:
        ...  # return base address


:func:`get_base_address_from_handle` is used for fetching base address of the process by handle::

    # this function is not implemented, for example, on windows
    def get_base_address_from_handle(process_handle: int) -> int:
        ...  # return base address


:func:`open_process` is used for getting process handle to use::

    def open_process(process_id: int) -> int:
        ...  # return handle to the process with ID of "process_id"


:func:`close_process` is used for closing process handle after use::

    def close_process(process_handle: int) -> None:
        ...  # can do nothing, if shutdown is not needed


:func:`get_process_id_from_name` is used to get process ID from process name::

    def get_process_id_from_name(process_name: str) -> int:
        ...


:func:`get_process_id_from_window_title` is used to get process ID from window title::

    def get_process_id_from_window_title(window_title: str) -> int:
        ...


:func:`get_process_name_from_id` is used to get process name from process ID::

    def get_process_name_from_id(process_id: int) -> str:
        ...


:func:`inject_dll` is used to inject DLL into process::

    def inject_dll(process_id: int, path: Union[Path, str]) -> bool:
        ...


:func:`terminate_process` is used to terminate the process::

    def terminate_process(process_handle: int) -> bool:
        ...


:func:`get_process_bits` is used to determine process bitness::

    def get_process_bits(process_id: int) -> int:
        ...  # return process bits here


:func:`get_process_bits_from_handle` is same as above, except it uses process handle instead::

    def get_process_bits_from_handle(process_handle: int) -> int:
        ...  # return process bits here


:func:`protect_process_memory` is used to override memory protection::

    def protect_process_memory(
        process_handle: int, address: int, size: int, flags: gd.Protection
    ) -> int:
        # note: "flags" should default to read, write and execute permissions
        ...


:func:`read_process_memory` is used to read memory of the process::

    def read_process_memory(process_handle: int, address: int, size: int) -> bytes:
        ...  # return data that was read


:func:`write_process_memory` is used to write memory to the process::

    def write_process_memory(process_handle: int, address: int, data: bytes) -> int:
        ...  # return how many bytes were written
"""

from gd.code_utils import unimplemented
from gd.platform import ANDROID, IOS, LINUX, MACOS, WINDOWS

try:
    from gd.memory.linux import (  # type: ignore
        allocate_memory as linux_allocate_memory,
        free_memory as linux_free_memory,
        get_base_address as linux_get_base_address,
        get_base_address_from_handle as linux_get_base_address_from_handle,
        get_process_bits as linux_get_process_bits,
        get_process_bits_from_handle as linux_get_process_bits_from_handle,
        open_process as linux_open_process,
        close_process as linux_close_process,
        get_process_id_from_name as linux_get_process_id_from_name,
        get_process_id_from_window_title as linux_get_process_id_from_window_title,
        get_process_name_from_id as linux_get_process_name_from_id,
        inject_dll as linux_inject_dll,
        terminate_process as linux_terminate_process,
        protect_process_memory as linux_protect_process_memory,
        read_process_memory as linux_read_process_memory,
        write_process_memory as linux_write_process_memory,
    )

except ImportError:
    linux_allocate_memory = unimplemented
    linux_free_memory = unimplemented
    linux_get_base_address = unimplemented
    linux_get_base_address_from_handle = unimplemented
    linux_get_process_bits = unimplemented
    linux_get_process_bits_from_handle = unimplemented
    linux_open_process = unimplemented
    linux_close_process = unimplemented
    linux_get_process_id_from_name = unimplemented
    linux_get_process_id_from_window_title = unimplemented
    linux_get_process_name_from_id = unimplemented
    linux_inject_dll = unimplemented
    linux_terminate_process = unimplemented
    linux_protect_process_memory = unimplemented
    linux_read_process_memory = unimplemented
    linux_write_process_memory = unimplemented

try:
    from gd.memory.macos import (  # type: ignore
        allocate_memory as macos_allocate_memory,
        free_memory as macos_free_memory,
        get_base_address as macos_get_base_address,
        get_base_address_from_handle as macos_get_base_address_from_handle,
        get_process_bits as macos_get_process_bits,
        get_process_bits_from_handle as macos_get_process_bits_from_handle,
        open_process as macos_open_process,
        close_process as macos_close_process,
        get_process_id_from_name as macos_get_process_id_from_name,
        get_process_id_from_window_title as macos_get_process_id_from_window_title,
        get_process_name_from_id as macos_get_process_name_from_id,
        inject_dll as macos_inject_dll,
        terminate_process as macos_terminate_process,
        protect_process_memory as macos_protect_process_memory,
        read_process_memory as macos_read_process_memory,
        write_process_memory as macos_write_process_memory,
    )

except ImportError:
    macos_allocate_memory = unimplemented
    macos_free_memory = unimplemented
    macos_get_base_address = unimplemented
    macos_get_base_address_from_handle = unimplemented
    macos_get_process_bits = unimplemented
    macos_get_process_bits_from_handle = unimplemented
    macos_open_process = unimplemented
    macos_close_process = unimplemented
    macos_get_process_id_from_name = unimplemented
    macos_get_process_id_from_window_title = unimplemented
    macos_get_process_name_from_id = unimplemented
    macos_inject_dll = unimplemented
    macos_terminate_process = unimplemented
    macos_protect_process_memory = unimplemented
    macos_read_process_memory = unimplemented
    macos_write_process_memory = unimplemented

try:
    from gd.memory.windows import (  # type: ignore
        allocate_memory as windows_allocate_memory,
        free_memory as windows_free_memory,
        get_base_address as windows_get_base_address,
        get_base_address_from_handle as windows_get_base_address_from_handle,
        get_process_bits as windows_get_process_bits,
        get_process_bits_from_handle as windows_get_process_bits_from_handle,
        open_process as windows_open_process,
        close_process as windows_close_process,
        get_process_id_from_name as windows_get_process_id_from_name,
        get_process_id_from_window_title as windows_get_process_id_from_window_title,
        get_process_name_from_id as windows_get_process_name_from_id,
        inject_dll as windows_inject_dll,
        terminate_process as windows_terminate_process,
        protect_process_memory as windows_protect_process_memory,
        read_process_memory as windows_read_process_memory,
        write_process_memory as windows_write_process_memory,
    )

except ImportError:
    windows_allocate_memory = unimplemented
    windows_free_memory = unimplemented
    windows_get_base_address = unimplemented
    windows_get_base_address_from_handle = unimplemented
    windows_get_process_bits = unimplemented
    windows_get_process_bits_from_handle = unimplemented
    windows_open_process = unimplemented
    windows_close_process = unimplemented
    windows_get_process_id_from_name = unimplemented
    windows_get_process_id_from_window_title = unimplemented
    windows_get_process_name_from_id = unimplemented
    windows_inject_dll = unimplemented
    windows_terminate_process = unimplemented
    windows_protect_process_memory = unimplemented
    windows_read_process_memory = unimplemented
    windows_write_process_memory = unimplemented


if ANDROID or LINUX:
    allocate_memory = linux_allocate_memory
    free_memory = linux_free_memory
    get_base_address = linux_get_base_address
    get_base_address_from_handle = linux_get_base_address_from_handle
    get_process_bits = linux_get_process_bits
    get_process_bits_from_handle = linux_get_process_bits_from_handle
    open_process = linux_open_process
    close_process = linux_close_process
    get_process_id_from_name = linux_get_process_id_from_name
    get_process_id_from_window_title = linux_get_process_id_from_window_title
    get_process_name_from_id = linux_get_process_name_from_id
    inject_dll = linux_inject_dll
    terminate_process = linux_terminate_process
    protect_process_memory = linux_protect_process_memory
    read_process_memory = linux_read_process_memory
    write_process_memory = linux_write_process_memory


elif IOS or MACOS:
    allocate_memory = macos_allocate_memory
    free_memory = macos_free_memory
    get_base_address = macos_get_base_address
    get_base_address_from_handle = macos_get_base_address_from_handle
    get_process_bits = macos_get_process_bits
    get_process_bits_from_handle = macos_get_process_bits_from_handle
    open_process = macos_open_process
    close_process = macos_close_process
    get_process_id_from_name = macos_get_process_id_from_name
    get_process_id_from_window_title = macos_get_process_id_from_window_title
    get_process_name_from_id = macos_get_process_name_from_id
    inject_dll = macos_inject_dll
    terminate_process = macos_terminate_process
    protect_process_memory = macos_protect_process_memory
    read_process_memory = macos_read_process_memory
    write_process_memory = macos_write_process_memory

elif WINDOWS:
    allocate_memory = windows_allocate_memory
    free_memory = windows_free_memory
    get_base_address = windows_get_base_address
    get_base_address_from_handle = windows_get_base_address_from_handle
    get_process_bits = windows_get_process_bits
    get_process_bits_from_handle = windows_get_process_bits_from_handle
    open_process = windows_open_process
    close_process = windows_close_process
    get_process_id_from_name = windows_get_process_id_from_name
    get_process_id_from_window_title = windows_get_process_id_from_window_title
    get_process_name_from_id = windows_get_process_name_from_id
    inject_dll = windows_inject_dll
    terminate_process = windows_terminate_process
    protect_process_memory = windows_protect_process_memory
    read_process_memory = windows_read_process_memory
    write_process_memory = windows_write_process_memory

else:
    import warnings

    warnings.warn("Memory API is not supported on this system.", Warning)

    allocate_memory = unimplemented
    free_memory = unimplemented
    get_base_address = unimplemented
    get_base_address_from_handle = unimplemented
    get_process_bits = unimplemented
    get_process_bits_from_handle = unimplemented
    open_process = unimplemented
    close_process = unimplemented
    get_process_id_from_name = unimplemented
    get_process_id_from_window_title = unimplemented
    get_process_name_from_id = unimplemented
    inject_dll = unimplemented
    terminate_process = unimplemented
    protect_process_memory = unimplemented
    read_process_memory = unimplemented
    write_process_memory = unimplemented


__all__ = (  # noqa
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
    "linux_allocate_memory",
    "linux_free_memory",
    "linux_get_base_address",
    "linux_get_base_address_from_handle",
    "linux_get_process_bits",
    "linux_get_process_bits_from_handle",
    "linux_open_process",
    "linux_close_process",
    "linux_get_process_id_from_name",
    "linux_get_process_id_from_window_title",
    "linux_get_process_name_from_id",
    "linux_inject_dll",
    "linux_terminate_process",
    "linux_protect_process_memory",
    "linux_read_process_memory",
    "linux_write_process_memory",
    "macos_allocate_memory",
    "macos_free_memory",
    "macos_get_base_address",
    "macos_get_base_address_from_handle",
    "macos_get_process_bits",
    "macos_get_process_bits_from_handle",
    "macos_open_process",
    "macos_close_process",
    "macos_get_process_id_from_name",
    "macos_get_process_id_from_window_title",
    "macos_get_process_name_from_id",
    "macos_inject_dll",
    "macos_terminate_process",
    "macos_protect_process_memory",
    "macos_read_process_memory",
    "macos_write_process_memory",
    "windows_allocate_memory",
    "windows_free_memory",
    "windows_get_base_address",
    "windows_get_base_address_from_handle",
    "windows_get_process_bits",
    "windows_get_process_bits_from_handle",
    "windows_open_process",
    "windows_close_process",
    "windows_get_process_id_from_name",
    "windows_get_process_id_from_window_title",
    "windows_get_process_name_from_id",
    "windows_inject_dll",
    "windows_terminate_process",
    "windows_protect_process_memory",
    "windows_read_process_memory",
    "windows_write_process_memory",
)
