from operator import attrgetter

from gd.typing import Callable, Iterable, List, Optional, Set, TypeVar, Union, cast

__all__ = ("find", "get", "unique")

T = TypeVar("T")
U = TypeVar("U")


def unique(iterable: Iterable[T]) -> List[T]:
    """Return a list of all unique elements in iterable.

    This function preserves order of elements.

    Example:

    .. code-block:: python3

        unique([3, 2, 1, 1, 2]) -> [3, 2, 1]
    """
    seen: Set[T] = set()
    add_to_seen = seen.add
    return [element for element in iterable if not (element in seen or add_to_seen(element))]


def find(
    predicate: Callable[[T], bool], iterable: Iterable[T], *, find_all: bool = False
) -> Optional[Union[T, List[T]]]:
    """For each element in iterable, return first element if predicate
    returns ``True`` and ``'find_all'`` is ``False``.

    Otherwise, find all elements matching and return them.

    Example:

    .. code-block:: python3

        ...
        friends = await client.get_friends()
        old_users = gd.utils.find(lambda x: x.account_id < 500000, friends, find_all=True)

    """
    if not find_all:
        for element in iterable:
            if predicate(element):
                return element

        return None  # for some reason mypy expects us to do this

    else:
        return list(filter(predicate, iterable))


def get(iterable: Iterable[T], **attributes: U) -> Optional[Union[T, List[T]]]:
    """For each element in iterable, return first element that matches
    requirements and ``find_all`` is ``False``.

    Otherwise, find all elements matching and return them.

    Example:

    .. code-block:: python3

        friends = await client.get_friends()
        nekit = gd.search_utils.get(friends, name="NeKitDS")

    """
    find_all = attributes.pop("find_all", cast(U, False))

    converted = [
        (attrgetter(attribute.replace("__", ".")), value) for attribute, value in attributes.items()
    ]

    if not find_all:
        for element in iterable:
            if all(predicate(element) == value for predicate, value in converted):
                return element

        return None  # for some reason mypy expects us to do this

    else:
        return list(
            filter(
                lambda element: all(predicate(element) == value for predicate, value in converted),
                iterable,
            )
        )
