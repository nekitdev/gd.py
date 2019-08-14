from operator import attrgetter as attrget

def find(predicate, seq, *, _all: bool = False):
    """For each element in sequence, return first element if predicate
    returns ``True`` and ``'_all'`` is ``False``.

    Otherwise, find all elements matching and return them.

    Example:

    .. code-block:: python3

        ...
        friends = await client.get_friends()
        old_users = gd.utils.find(lambda x: x.account_id < 500_000, friends, _all=True)

    """
    res = []
    for elem in seq:
        if predicate(elem):
            if not _all:
                return elem
            res.append(elem)

    return None if not res else res


def get(iterable, **attrs):
    """For each element in iterable, return first element that matches
    requirements and ``'_all'`` is ``False``.

    Otherwise, find all elements matching and return them.

    Example:

    .. code-block:: python3

        ...
        friends = await client.get_friends()
        nekit = gd.utils.get(friends, name='NeKitDS')

    """
    # check if ALL elements matching requirements should be returned
    _all = attrs.pop("_all", False)

    converted = [
        (attrget(attr.replace('__', '.')), value)
        for attr, value in attrs.items()
    ]

    res = []
    for elem in iterable:
        if all(pred(elem) == value for pred, value in converted):
            if not _all:
                return elem
            res.append(elem)

    return None if not res else res
