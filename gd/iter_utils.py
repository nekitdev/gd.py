from typing import Any, Callable, Dict, Iterable, Mapping, Tuple, TypeVar, Union, cast, overload

__all__ = ("extract_iterable_from_tuple", "is_iterable", "item_to_tuple", "mapping_merge")

KT = TypeVar("KT")
VT = TypeVar("VT")

T = TypeVar("T")


def mapping_merge(*mappings: Mapping[KT, VT], **arguments: VT) -> Dict[KT, VT]:
    final: Dict[KT, VT] = {}

    for mapping in mappings:
        final.update(mapping)

    final.update(arguments)  # type: ignore

    return final


def is_iterable(maybe_iterable: Union[Iterable[T], T], use_iter: bool = True) -> bool:
    if use_iter:
        try:
            iter(maybe_iterable)  # type: ignore
            return True

        except TypeError:  # "T" object is not iterable
            return False

    return isinstance(maybe_iterable, Iterable)


@overload  # noqa
def item_to_tuple(item: Iterable[T]) -> Tuple[T, ...]:  # noqa
    ...


@overload  # noqa
def item_to_tuple(item: T) -> Tuple[T, ...]:  # noqa
    ...


def item_to_tuple(item: Union[T, Iterable[T]]) -> Tuple[T, ...]:  # noqa
    if is_iterable(item):
        return tuple(cast(Iterable[T], item))

    return (cast(T, item),)


@overload  # noqa
def extract_iterable_from_tuple(  # noqa
    tuple_to_extract: Tuple[Iterable[T]], check: Callable[[Any], bool]
) -> Iterable[T]:
    ...


@overload  # noqa
def extract_iterable_from_tuple(  # noqa
    tuple_to_extract: Tuple[T, ...], check: Callable[[Any], bool]
) -> Iterable[T]:
    ...


def extract_iterable_from_tuple(  # noqa
    tuple_to_extract: Union[Tuple[Iterable[T]], Tuple[T, ...]],
    check: Callable[[Any], bool] = is_iterable,
) -> Iterable[T]:
    if len(tuple_to_extract) == 1:
        maybe_return = tuple_to_extract[0]

        if check(maybe_return):
            return cast(Iterable[T], maybe_return)

    return cast(Iterable[T], tuple_to_extract)
