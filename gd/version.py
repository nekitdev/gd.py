import sys

from typing_extensions import Final
from versions import PreTag, Version, parse_version

from gd import __version__ as version

__all__ = ("version_info", "python_version_info")

version_info = parse_version(version)

FINAL: Final[str] = "final"

python_major, python_minor, python_micro, python_phase, python_value = sys.version_info

if python_phase == FINAL:
    python_version_info = Version.from_parts(python_major, python_minor, python_micro)

else:
    python_version_info = Version.from_parts(
        python_major,
        python_minor,
        python_micro,
        pre=PreTag(python_phase, python_value).normalize(),
    )
