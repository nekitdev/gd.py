import sys

__all__ = ("PLATFORM", "LINUX", "MACOS", "WINDOWS")

PLATFORM = sys.platform

WINDOWS = False
MACOS = False
LINUX = False

if PLATFORM.startswith("win"):
    WINDOWS = True

elif PLATFORM.startswith("darwin"):
    MACOS = True

elif PLATFORM.startswith("linux"):
    LINUX = True
