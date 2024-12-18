from gd.internals.robtop.core import concat_iterable_with, split_iterable_with

LEGACY_CAPACITY_SEPARATOR = "_"
CAPACITY_SEPARATOR = ","


def migrate_capacity(string: str) -> str:
    return string.replace(LEGACY_CAPACITY_SEPARATOR, CAPACITY_SEPARATOR)


split_capacity = split_iterable_with(CAPACITY_SEPARATOR)
concat_capacity = concat_iterable_with(CAPACITY_SEPARATOR)
