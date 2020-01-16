from .._typing import Any, Dict, Sequence

__all__ = ('mapper', 'MapperUtil', 'pad')


def convert(obj: Any) -> Any:
    try:
        return int(obj)
    except Exception:
        return obj


class MapperUtil:
    @staticmethod
    def map(item: Sequence, try_convert: bool = True) -> Dict[Any, Any]:
        mapping = zip(item[::2], item[1::2])

        if try_convert:
            res = {convert(key): convert(value) for key, value in mapping}

        else:
            res = {convert(key): value for key, value in mapping}

        return res


mapper = MapperUtil()
