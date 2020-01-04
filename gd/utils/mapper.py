from .._typing import Any, Dict, Iterable

__all__ = ('mapper', 'MapperUtil', 'pad')


def convert(obj: Any) -> Any:
    try:
        return int(obj)
    except Exception:
        return obj


class MapperUtil:
    @staticmethod
    def map(item: Iterable, try_convert: bool = True) -> Dict[Any, Any]:
        mapping = zip(item[::2], item[1::2])

        if try_convert:
            res = {convert(key): convert(value) for key, value in mapping}

        else:
            res = {convert(key): value for key, value in mapping}

        return res

    @staticmethod
    def normalize(item: str) -> str:
        res = str(item).replace('-', '+').replace('_', '/')
        return pad(res)

    @staticmethod
    def prepare_sending(item: str) -> str:
        res = str(item).replace('+', '-').replace('/', '_')
        return pad(res)


mapper = MapperUtil()


def pad(res: str, *, char: str = '=') -> str:
    # pad a string to be divisible by 4
    while len(res) % 4:
        res += char

    return res
