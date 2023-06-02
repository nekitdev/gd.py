from versions.meta import python_version_info
from versions.versioned import get_version

import gd

__all__ = ("version_info", "python_version_info")

version_info = get_version(gd)  # type: ignore
