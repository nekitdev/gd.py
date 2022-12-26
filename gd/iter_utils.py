from typing import Any, Dict, Hashable, Mapping, Sized, Tuple, TypeVar, overload

__all__ = ("contains_only_item", "mapping_merge", "unary_tuple", "unpack_unary_tuple")

Q = TypeVar("Q", bound=Hashable)
T = TypeVar("T")


@overload
def mapping_merge(*mappings: Mapping[str, T], **arguments: T) -> Dict[str, T]:
    ...


@overload
def mapping_merge(*mappings: Mapping[Q, T]) -> Dict[Q, T]:
    ...


def mapping_merge(*mappings: Mapping[Any, Any], **arguments: Any) -> Dict[Any, Any]:
    final: Dict[Any, Any] = {}

    for mapping in mappings:
        final.update(mapping)

    final.update(arguments)

    return final


def unary_tuple(item: T) -> Tuple[T]:
    return (item,)


def unpack_unary_tuple(tuple: Tuple[T]) -> T:
    (item,) = tuple

    return item


ONE = 1


def contains_only_item(sized: Sized) -> bool:
    return len(sized) == ONE
