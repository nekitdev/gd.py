from operator import attrgetter as attrget

from ..typing import Any, Callable, Iterable, List, Union

__all__ = ('find', 'get', 'unique')


def unique(iterable: Iterable) -> List[Any]:
    """Return a list of all unique elements in iterable.

    This function preserves order of elements.

    Example:

    .. code-block:: python3

        unique([3, 2, 1, 1, 2]) -> [3, 2, 1]
    """
    seen = set()
    f = seen.add
    return list(x for x in iterable if not (x in seen or f(x)))


def find(
    predicate: Callable[[Any], bool], iterable: Iterable, *,
    find_all: bool = False
) -> Union[Any, List[Any]]:
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
        for elem in iterable:
            if predicate(elem):
                return elem

    else:
        return list(filter(predicate, iterable))


def get(iterable: Iterable, **attrs: Any) -> Union[Any, List[Any]]:
    """For each element in iterable, return first element that matches
    requirements and ``'find_all'`` is ``False``.

    Otherwise, find all elements matching and return them.

    Example:

    .. code-block:: python3

        ...
        friends = await client.get_friends()
        nekit = gd.utils.get(friends, name='NeKitDS')

    """
    # check if ALL elements matching requirements should be returned
    find_all = attrs.pop("find_all", False)

    converted = [
        (attrget(attr.replace('__', '.')), value)
        for attr, value in attrs.items()
    ]

    if not find_all:
        for elem in iterable:
            if all(pred(elem) == value for pred, value in converted):
                return elem

    else:
        return list(filter(
            lambda elem: all(pred(elem) == value for pred, value in converted), iterable
        ))
