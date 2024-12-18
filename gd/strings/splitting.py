from typing import List

from typing_aliases import Parse

__all__ = ("split_checked", "split_at", "split_whitespace")


def split_checked(separator: str, string: str) -> List[str]:
    if not string:
        return []

    return string.split(separator)


def split_at(separator: str) -> Parse[List[str]]:
    def split(string: str) -> List[str]:
        return split_checked(separator, string)

    return split


def split_whitespace(string: str) -> List[str]:
    return string.split()
