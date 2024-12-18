from typing_aliases import Binary

from gd.strings.concatenation import concat_empty
from gd.strings.constants import BACKSLASH, BRACES, EMPTY
from gd.strings.splitting import split_whitespace

create_translation = str.maketrans
dict_from_keys = dict.fromkeys

removing_braces = create_translation(dict_from_keys(BRACES, EMPTY))


def remove_braces(string: str) -> str:
    return string.translate(removing_braces)


remove_prefix: Binary[str, str, str]
remove_suffix: Binary[str, str, str]


try:
    remove_prefix = str.removeprefix
    remove_suffix = str.removesuffix

except AttributeError:

    def remove_prefix(self: str, prefix: str) -> str:
        if self.startswith(prefix):
            return self[len(prefix) :]

        return self

    def remove_suffix(self: str, suffix: str) -> str:
        if self.endswith(suffix):
            return self[: -len(suffix)]

        return self


def remove_escapes(string: str) -> str:
    return string.replace(BACKSLASH, EMPTY)


def remove_whitespace(string: str) -> str:
    return concat_empty(split_whitespace(string))
