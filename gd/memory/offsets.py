from gd.json import NamedDict

__all__ = (
    "linux_offsets",
    "macos_offsets",
    "windows_offsets",
)

windows_offsets: NamedDict[str, int] = NamedDict(
    game_manager=0x3222D0,
    play_layer=0x164,
    level_settings=0x22C,
    level=0x114,
    level_name=0xFC,
)

macos_offsets: NamedDict[str, int] = NamedDict(
    game_manager=0x69E398,
    play_layer=0x180,
    level_settings=0x390,
    level=0x150,
    level_name=0x138,
)

linux_offsets: NamedDict[str, int] = NamedDict()
