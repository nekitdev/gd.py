from gd.internals.robtop.core import concat_iterable_with, split_iterable_with

DEMON_INFO_SEPARATOR = ","
LEVEL_INFO_SEPARATOR = ","
PLATFORMER_INFO_SEPARATOR = ","

split_demon_info = split_iterable_with(DEMON_INFO_SEPARATOR)
concat_demon_info = concat_iterable_with(DEMON_INFO_SEPARATOR)

split_level_info = split_iterable_with(LEVEL_INFO_SEPARATOR)
concat_level_info = concat_iterable_with(LEVEL_INFO_SEPARATOR)

split_platformer_info = split_iterable_with(PLATFORMER_INFO_SEPARATOR)
concat_platformer_info = concat_iterable_with(PLATFORMER_INFO_SEPARATOR)
