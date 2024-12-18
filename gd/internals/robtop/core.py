from typing import Iterable, Mapping, Tuple

from funcs.unpacking import unpack_binary
from iters.iters import iter
from typing_aliases import Pair, Parse, StringMapping, Unary

from gd.strings.splitting import split_checked


def bool_str(value: bool) -> str:
    return str(int(value))


def float_str(value: float) -> str:
    whole = int(value)

    return str(whole) if whole == value else str(value)


def int_bool(string: str) -> bool:
    return bool(int(string)) if string else False


def int_left(left: str, right: str) -> Tuple[int, str]:
    return (int(left), right)


def str_left(left: int, right: str) -> Pair[str]:
    return (str(left), right)


unpack_int_left = unpack_binary(int_left)
unpack_str_left = unpack_binary(str_left)


def split_iterable(separator: str, string: str) -> Iterable[str]:
    return split_checked(separator, string)


def split_iterable_with(separator: str) -> Parse[Iterable[str]]:
    def split(string: str) -> Iterable[str]:
        return split_iterable(separator, string)

    return split


def concat_iterable(separator: str, iterable: Iterable[str]) -> str:
    return separator.join(iterable)


def concat_iterable_with(separator: str) -> Unary[Iterable[str], str]:
    def concat(iterable: Iterable[str]) -> str:
        return concat_iterable(separator, iterable)

    return concat


def split_string_mapping(separator: str, string: str) -> StringMapping[str]:
    return iter(split_iterable(separator, string)).pairs().dict()


def split_string_mapping_with(separator: str) -> Parse[StringMapping[str]]:
    def split(string: str) -> StringMapping[str]:
        return split_string_mapping(separator, string)

    return split


def string_mapping_to_iterable(mapping: StringMapping[str]) -> Iterable[str]:
    return iter(mapping.items()).flatten().unwrap()


def concat_string_mapping(separator: str, mapping: StringMapping[str]) -> str:
    return separator.join(string_mapping_to_iterable(mapping))


def concat_string_mapping_with(separator: str) -> Unary[StringMapping[str], str]:
    def concat(mapping: StringMapping[str]) -> str:
        return concat_string_mapping(separator, mapping)

    return concat


def split_mapping(separator: str, string: str) -> Mapping[int, str]:
    return iter(split_iterable(separator, string)).pairs().map(unpack_int_left).dict()


def split_mapping_with(separator: str) -> Parse[Mapping[int, str]]:
    def split(string: str) -> Mapping[int, str]:
        return split_mapping(separator, string)

    return split


def mapping_to_iterable(mapping: Mapping[int, str]) -> Iterable[str]:
    return iter(mapping.items()).map(unpack_str_left).flatten().unwrap()


def concat_mapping(separator: str, mapping: Mapping[int, str]) -> str:
    return separator.join(mapping_to_iterable(mapping))


def concat_mapping_with(separator: str) -> Unary[Mapping[int, str], str]:
    def concat(mapping: Mapping[int, str]) -> str:
        return concat_mapping(separator, mapping)

    return concat
