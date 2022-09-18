from versions import parse_version, python_version_info

from gd import __version__ as version

__all__ = ("version_info", "python_version_info")

version_info = parse_version(version)
