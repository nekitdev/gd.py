"""Internal memory interfaces for different platforms.

## Functions

- `open`
- `close`
- `terminate`
- `allocate`
- `free`
- `protect`
- `read`
- `write`
- `get_base_address`
- `get_base_address_from_handle`?
- `get_process_bits`
- `get_process_bits_from_handle`?
- `get_process_id_from_name`
- `get_process_id_from_title`?
"""

from typing import Any

from typing_extensions import Never

from gd.platform import DARWIN, WINDOWS

UNIMPLEMENTED = "this function is not implemented"


def unimplemented(*args: Any, **kwargs: Any) -> Never:
    raise NotImplementedError(UNIMPLEMENTED)


try:
    from gd.memory.internal.darwin import allocate as darwin_allocate
    from gd.memory.internal.darwin import close as darwin_close
    from gd.memory.internal.darwin import free as darwin_free
    from gd.memory.internal.darwin import get_base_address as darwin_get_base_address
    from gd.memory.internal.darwin import (
        get_base_address_from_handle as darwin_get_base_address_from_handle
    )
    from gd.memory.internal.darwin import get_process_bits as darwin_get_process_bits
    from gd.memory.internal.darwin import (
        get_process_bits_from_handle as darwin_get_process_bits_from_handle
    )
    from gd.memory.internal.darwin import (
        get_process_id_from_name as darwin_get_process_id_from_name
    )
    from gd.memory.internal.darwin import (
        get_process_id_from_title as darwin_get_process_id_from_title
    )
    from gd.memory.internal.darwin import open as darwin_open
    from gd.memory.internal.darwin import protect as darwin_protect
    from gd.memory.internal.darwin import read as darwin_read
    from gd.memory.internal.darwin import terminate as darwin_terminate
    from gd.memory.internal.darwin import write as darwin_write

except ImportError:
    darwin_allocate = unimplemented
    darwin_close = unimplemented
    darwin_free = unimplemented
    darwin_get_base_address = unimplemented
    darwin_get_base_address_from_handle = unimplemented
    darwin_get_process_bits = unimplemented
    darwin_get_process_bits_from_handle = unimplemented
    darwin_get_process_id_from_name = unimplemented
    darwin_get_process_id_from_title = unimplemented
    darwin_open = unimplemented
    darwin_protect = unimplemented
    darwin_read = unimplemented
    darwin_terminate = unimplemented
    darwin_write = unimplemented

try:
    from gd.memory.internal.windows import allocate as windows_allocate
    from gd.memory.internal.windows import close as windows_close
    from gd.memory.internal.windows import free as windows_free
    from gd.memory.internal.windows import get_base_address as windows_get_base_address
    from gd.memory.internal.windows import (
        get_base_address_from_handle as windows_get_base_address_from_handle
    )
    from gd.memory.internal.windows import get_process_bits as windows_get_process_bits
    from gd.memory.internal.windows import (
        get_process_bits_from_handle as windows_get_process_bits_from_handle
    )
    from gd.memory.internal.windows import (
        get_process_id_from_name as windows_get_process_id_from_name
    )
    from gd.memory.internal.windows import (
        get_process_id_from_title as windows_get_process_id_from_title
    )
    from gd.memory.internal.windows import open as windows_open
    from gd.memory.internal.windows import protect as windows_protect
    from gd.memory.internal.windows import read as windows_read
    from gd.memory.internal.windows import terminate as windows_terminate
    from gd.memory.internal.windows import write as windows_write

except ImportError:
    windows_allocate = unimplemented
    windows_close = unimplemented
    windows_free = unimplemented
    windows_get_base_address = unimplemented
    windows_get_base_address_from_handle = unimplemented
    windows_get_process_bits = unimplemented
    windows_get_process_bits_from_handle = unimplemented
    windows_get_process_id_from_name = unimplemented
    windows_get_process_id_from_title = unimplemented
    windows_open = unimplemented
    windows_protect = unimplemented
    windows_read = unimplemented
    windows_terminate = unimplemented
    windows_write = unimplemented

system_allocate = unimplemented
system_close = unimplemented
system_free = unimplemented
system_get_base_address = unimplemented
system_get_base_address_from_handle = unimplemented
system_get_process_bits = unimplemented
system_get_process_bits_from_handle = unimplemented
system_get_process_id_from_name = unimplemented
system_get_process_id_from_title = unimplemented
system_open = unimplemented
system_protect = unimplemented
system_read = unimplemented
system_terminate = unimplemented
system_write = unimplemented

if DARWIN:
    system_allocate = darwin_allocate
    system_close = darwin_close
    system_free = darwin_free
    system_get_base_address = darwin_get_base_address
    system_get_base_address_from_handle = darwin_get_base_address_from_handle
    system_get_process_bits = darwin_get_process_bits
    system_get_process_bits_from_handle = darwin_get_process_bits_from_handle
    system_get_process_id_from_name = darwin_get_process_id_from_name
    system_get_process_id_from_title = darwin_get_process_id_from_title
    system_open = darwin_open
    system_protect = darwin_protect
    system_read = darwin_read
    system_terminate = darwin_terminate
    system_write = darwin_write

if WINDOWS:
    system_allocate = windows_allocate
    system_close = windows_close
    system_free = windows_free
    system_get_base_address = windows_get_base_address
    system_get_base_address_from_handle = windows_get_base_address_from_handle
    system_get_process_bits = windows_get_process_bits
    system_get_process_bits_from_handle = windows_get_process_bits_from_handle
    system_get_process_id_from_name = windows_get_process_id_from_name
    system_get_process_id_from_title = windows_get_process_id_from_title
    system_open = windows_open
    system_protect = windows_protect
    system_read = windows_read
    system_terminate = windows_terminate
    system_write = windows_write
