"""Internal memory interfaces for different platforms.

Every module should define several functions and classes.

Classes
-------
:class:`BaseProcessHandle` instances are used for any operation on processes.

:class:`BaseProcessID` instances represent IDs of processes.

Functions
---------
:func:`allocate_memory` is used for allocating memory::

    def allocate_memory(handle: BaseProcessHandle, size: int, address: int) -> int:
        ...  # allocate "size" bytes, trying to start at "address", and return address to memory


:func:`get_base_address` is used for fetching base address of some module::

    def get_base_address(process_id: BaseProcessID, module_name: str) -> int:
        ...  # return base address


:func:`open_process` is used for getting :class:`BaseProcessHandle` to use::

    def open_process(process_id: BaseProcessID) -> BaseProcessHandle:
        ...  # return handle to the process with ID of "process_id"


:func:`close_process` is used for closing :class:`BaseProcessHandle` after use::

    def close_process(process_handle: BaseProcessHandle) -> None:
        ...  # can do nothing, if shutdown is not needed


:func:`get_process_id_from_name` is used to get :class:`BaseProcessID` from process name::

    def get_process_id_from_name(process_name: str) -> BaseProcessID:
        ...


:func:`inject_dll` is used to inject DLL into process::

    def inject_dll(process_handle: BaseProcessHandle, path: Union[Path, str]) -> None:
        ...


:func:`terminate_process` is used to terminate the process::

    def terminate_process(process_handle: BaseProcessHandle) -> None:
        ...


:func:`read_process_memory` is used to read memory of the process::

    def read_process_memory(process_handle: BaseProcessHandle, address: int, size: int) -> bytes:
        ...  # return data that was read


:func:`write_process_memory` is used to write memory to the process::

    def write_process_memory(process_handle: BaseProcessHandle, address: int, data: bytes) -> int:
        ...  # return how many bytes were written
"""
