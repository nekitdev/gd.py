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
