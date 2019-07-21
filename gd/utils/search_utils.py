from operator import attrgetter as attrget

def find(predicate, seq, *, _all=False):
    res = []
    # for each element in sequence,
    # return element if predicate returns True and '_all' is False;
    # append it to 'res' otherwise.
    for elem in seq:
        if predicate(elem):
            if not _all:
                return elem
            res.append(elem)

    return None if not res else res


def get(iterable, **attrs):
    # check if ALL elements matching requirements should be returned
    _all = attrs.pop("_all", False)

    converted = [
        (attrget(attr.replace('__', '.')), value)
        for attr, value in attrs.items()
    ]

    res = []
    # for each element in iterable,
    # return element if it matches requirements and '_all' is False;
    # append it to 'res' otherwise.
    for elem in iterable:
        if all(pred(elem) == value for pred, elem in converted):
            if not _all:
                return elem
            res.append(elem)

    return None if not res else res
