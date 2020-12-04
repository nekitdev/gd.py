# type: ignore

import ctypes
import ctypes.util

libc_name = ctypes.util.find_library("c")

if libc_name is None:
    raise ImportError("Can not define memory functions for Linux.")

libc = ctypes.CDLL(libc_name)  # type: ignore

pid_t = ctypes.c_int
