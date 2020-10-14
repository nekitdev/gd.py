import ctypes

kernel32 = ctypes.WinDLL("kernel32.dll")  # type: ignore
psapi = ctypes.WinDLL("psapi.dll")  # type: ignore
user32 = ctypes.WinDLL("user32.dll")  # type: ignore
