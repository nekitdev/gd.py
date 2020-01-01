from typing import Union
import json

__all__ = ('object_split', 'dump')


def _f(o: object):
    try:
        return o.__json__()
    except AttributeError:
        return o


def dump(x, **kwargs):
    return json.dumps(_dump(x), **kwargs)


def _dump(x):
    try:
        if isinstance(x, dict):
            return {_dump(k): _dump(v) for k, v in x.items()}

        elif isinstance(x, (list, tuple, set)):
            return list(_dump(e) for e in x)

        elif isinstance(x, (int, float, str)):
            return x

        elif x is None:
            return x

        return _dump(_f(x))

    except RecursionError:
        raise


def object_split(string: Union[bytes, str]):
    sc = ';' if isinstance(string, str) else b';'

    final = string.split(sc)
    final.pop(0)

    if string.endswith(sc):
        final.pop()

    return final
