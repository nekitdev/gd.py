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
    player=0x224,
    level_settings=0x22C,
    level=0x114,
    level_id=0xF8,
    level_name=0xFC,
    level_creator_name=0x144,
    level_difficulty_denominator=0x1E0,
    level_difficulty_numerator=0x1E4,
    level_attempts=0x218,
    level_jumps=0x224,
    level_normal_percent=0x248,
    level_practice_percent=0x26C,
    level_score=0x27C,
    level_epic=0x280,
    level_demon=0x29C,
    level_demon_difficulty=0x2A0,
    level_stars=0x2AC,
    level_auto=0x2B0,
    level_level_type_value=0x364,
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
