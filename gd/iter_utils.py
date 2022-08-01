from typing import Any, Dict, Hashable, Mapping, Tuple, TypeVar, overload

from typing_extensions import TypeVarTuple, Unpack

__all__ = ("mapping_merge", "tuple_args")

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


Args = TypeVarTuple("Args")


def tuple_args(*args: Unpack[Args]) -> Tuple[Unpack[Args]]:
    return args
