import ctypes

kernel32 = ctypes.WinDLL("kernel32.dll")
psapi = ctypes.WinDLL("psapi.dll")
user32 = ctypes.WinDLL("user32.dll")
