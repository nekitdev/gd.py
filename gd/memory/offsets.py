from gd.json import NamedDict
from gd.platform import LINUX, MACOS, WINDOWS

__all__ = (
    "offsets",
    "linux_offsets",
    "macos_offsets",
    "windows_offsets",
)


class Offsets(NamedDict[str, int]):
    def __getattr__(self, attr: str) -> int:
        try:
            return super().__getattr__(attr)

        except (AttributeError, KeyError):
            raise LookupError(f"Can not find offset {attr!r} in offsets.") from None


windows_offsets: Offsets = Offsets(
    game_manager=0x3222D0,
    play_layer=0x164,
    editor_layer=0x168,
    level_settings=0x22C,
    level=0x114,
    level_name=0xFC,
)

macos_offsets: Offsets = Offsets(
    game_manager=0x69E398,
    play_layer=0x180,
    editor_layer=0x188,
    level_settings=0x390,
    level=0x150,
    level_name=0x138,
)

linux_offsets: Offsets = Offsets()

offsets: Offsets = Offsets()

if LINUX:
    offsets = linux_offsets

elif MACOS:
    offsets = macos_offsets

elif WINDOWS:
    offsets = windows_offsets

else:
    pass
