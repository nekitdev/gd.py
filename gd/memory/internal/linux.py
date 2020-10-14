import ctypes.util
import ctypes

libc = ctypes.CDLL(ctypes.util.find_library("c"))  # type: ignore
