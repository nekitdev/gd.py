from gd.memory.data import Data
# from gd.memory.internal import (
#     allocate_memory as os_allocate_memory,
#     free_memory as os_free_memory,
#     get_base_address as os_get_base_address,
#     get_base_address_from_handle as os_get_base_address_from_handle,
#     open_process as os_open_process,
#     close_process as os_close_process,
#     get_process_id_from_name as os_get_process_id_from_name,
#     inject_dll as os_inject_dll,
#     terminate_process as os_terminate_process,
#     protect_process_memory as os_protect_process_memory,
#     read_process_memory as os_read_process_memory,
#     write_process_memory as os_write_process_memory,
#     linux_allocate_memory,
#     linux_free_memory,
#     linux_get_base_address,
#     linux_get_base_address_from_handle,
#     linux_open_process,
#     linux_close_process,
#     linux_get_process_id_from_name,
#     linux_inject_dll,
#     linux_terminate_process,
#     linux_protect_process_memory,
#     linux_read_process_memory,
#     linux_write_process_memory,
#     macos_allocate_memory,
#     macos_free_memory,
#     macos_get_base_address,
#     macos_get_base_address_from_handle,
#     macos_open_process,
#     macos_close_process,
#     macos_get_process_id_from_name,
#     macos_inject_dll,
#     macos_terminate_process,
#     macos_protect_process_memory,
#     macos_read_process_memory,
#     macos_write_process_memory,
#     windows_allocate_memory,
#     windows_free_memory,
#     windows_get_base_address,
#     windows_get_base_address_from_handle,
#     windows_open_process,
#     windows_close_process,
#     windows_get_process_id_from_name,
#     windows_inject_dll,
#     windows_terminate_process,
#     windows_protect_process_memory,
#     windows_read_process_memory,
#     windows_write_process_memory,
# )


class State:
    def __init__(
        self,
        process_name: str,
        process_id: int,
        process_handle: int,
        base_address: int,
        pointer_type: Data[int],
    ) -> None:
        self._process_name = process_name
        self._process_id = process_id
        self._process_handle = process_handle
        self._pointer_type = pointer_type
        self._base_address = base_address

    @property
    def process_name(self) -> str:
        return self._process_name

    @property
    def process_id(self) -> int:
        return self._process_id

    @property
    def process_handle(self) -> int:
        return self._process_handle

    @property
    def pointer_type(self) -> Data[int]:
        return self._pointer_type

    @property
    def base_address(self) -> int:
        return self._base_address


class Layer:
    def __init__(self, address: int, state: State) -> None:
        self._address = address
        self._state = state
