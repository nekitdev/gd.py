from pathlib import Path

__all__ = (
    "ROOT",
    "ASSETS",
    "ICONS",
    "ANIMATIONS",
    "ROBOT_ANIMATIONS",
    "SPIDER_ANIMATIONS",
)

ROOT = Path(__file__).parent

ASSETS_NAME = "assets"

ASSETS = ROOT / ASSETS_NAME

ICONS_NAME = "icons"

ICONS = ASSETS / ICONS_NAME

ANIMATIONS_NAME = "animations"

ANIMATIONS = ICONS / ANIMATIONS_NAME

ROBOT = "robot"
SPIDER = "spider"

IMAGE_SUFFIX = ".png"
DATA_SUFFIX = ".json"

ROBOT_ANIMATIONS = (ANIMATIONS / ROBOT).with_suffix(DATA_SUFFIX)
SPIDER_ANIMATIONS = (ANIMATIONS / SPIDER).with_suffix(DATA_SUFFIX)
