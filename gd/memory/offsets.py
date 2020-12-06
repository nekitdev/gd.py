from gd.json import NamedDict
from gd.platform import LINUX, MACOS, WINDOWS
from gd.typing import TypeVar, cast

__all__ = (
    "offsets_x32",
    "offsets_x64",
    "linux_offsets_x32",
    "linux_offsets_x64",
    "macos_offsets_x32",
    "macos_offsets_x64",
    "windows_offsets_x32",
    "windows_offsets_x64",
)

OffsetT = TypeVar("OffsetT", int, "Offsets")


class Offsets(NamedDict[str, OffsetT]):
    def __getattr__(self, attr: str) -> OffsetT:
        try:
            return cast(OffsetT, super().__getattr__(attr))

        except (AttributeError, KeyError):
            raise LookupError(f"Can not find offset {attr!r} in offsets.") from None


windows_offsets_x32: Offsets = Offsets(
    game_manager=Offsets(
        play_layer=0x164, editor_layer=0x168, user_name=0x198, scene=0x1DC, offset=0x3222D0
    ),
    account_manager=Offsets(password=0xF0, user_name=0x108, offset=0x3222D8),
    base_game_layer=Offsets(player=0x224, level_settings=0x22C),
    play_layer=Offsets(dead=0x39C, level_length=0x3B4, practice_mode=0x495, attempt=0x4A8),
    editor_layer=Offsets(editor_ui=0x380, object_count=0x3A0),
    editor_ui=Offsets(),
    level_settings=Offsets(level=0x114),
    level=Offsets(
        id=0xF8,
        name=0xFC,
        description=0x114,
        creator_name=0x144,
        unprocessed_data=0x12C,
        difficulty_denominator=0x1E0,
        difficulty_numerator=0x1E4,
        attempts=0x218,
        jumps=0x224,
        normal_percent=0x248,
        practice_percent=0x26C,
        score=0x27C,
        epic=0x280,
        demon=0x29C,
        demon_difficulty=0x2A0,
        stars=0x2AC,
        auto=0x2B0,
        level_type=0x364,
    ),
    player=Offsets(gamemodes=0x638, flipped_gravity=0x63E, size=0x644, speed=0x648),
    node=Offsets(x=0x34, y=0x38),
)

windows_offsets_x64: Offsets = Offsets()

macos_offsets_x32: Offsets = Offsets()

macos_offsets_x64: Offsets = Offsets(
    game_manager=Offsets(play_layer=0x180, editor_layer=0x188, offset=0x3222D0),
    play_layer=Offsets(level_settings=0x390),
    editor_layer=Offsets(level_settings=0x390),
    level_settings=Offsets(level=0x150),
    level=Offsets(name=0x138),
    player=Offsets(),
)

linux_offsets_x32: Offsets = Offsets()
linux_offsets_x64: Offsets = Offsets()

offsets_x32: Offsets = Offsets()
offsets_x64: Offsets = Offsets()

if LINUX:
    offsets_x32 = linux_offsets_x32
    offsets_x64 = linux_offsets_x64

elif MACOS:
    offsets_x32 = macos_offsets_x32
    offsets_x64 = macos_offsets_x64

elif WINDOWS:
    offsets_x32 = windows_offsets_x32
    offsets_x64 = windows_offsets_x64

else:
    pass
