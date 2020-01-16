import json

from .._typing import Any, Dict, List, Optional, Union

__all__ = ('make_repr', 'object_split', 'dump')


def make_repr(obj: Any, info: Optional[Dict[Any, Any]] = None) -> str:
    """Create a nice __repr__ for the object."""
    if info is None:
        info = {}

    module = obj.__module__.split('.').pop(0)
    name = obj.__class__.__name__

    if not info:
        return '<{}.{}>'.format(module, name)

    final = (' '.join('{0}={1}'.format(*t) for t in info.items()))

    return '<{}.{} {}>'.format(module, name, final)


def dump(x: Any, **kwargs) -> str:
    return json.dumps(_dump(x), **kwargs)


def _dump(x: Any) -> Any:
    if hasattr(x, '__json__'):
        return _dump(x.__json__())

    elif isinstance(x, dict):
        return {_dump(k): _dump(v) for k, v in x.items()}

    elif isinstance(x, (list, tuple, set)):
        return list(_dump(e) for e in x)

    elif isinstance(x, (int, float, str)):
        return x

    elif x is None:
        return x

    else:
        raise TypeError('Object of type {0.__class__.__name__!r} is not JSON resizable.'.format(x))


def object_split(string: Union[bytes, str]) -> Union[List[bytes], List[str]]:
    sc = ';' if isinstance(string, str) else b';'  # type: ignore

    final = string.split(sc)  # type: ignore
    final.pop(0)

    if string.endswith(sc):  # type: ignore
        final.pop()

    return final
