from .wrap_tools import convert_to_type

__all__ = ('mapper_util', 'MapperUtil', 'pad', 'ceil')


class MapperUtil:
    @staticmethod
    def map(item):
        res = {}

        convert = lambda obj: convert_to_type(obj, int)

        for kv_tuple in zip(item[::2], item[1::2]):
            key, value = map(convert, kv_tuple)
            res[key] = value

        return res

    @staticmethod
    def normalize(item):
        res = str(item).replace('-', '+').replace('_', '/')
        return pad(res)

    @staticmethod
    def prepare_sending(item):
        res = str(item).replace('+', '-').replace('/', '_')
        return pad(res)

mapper_util = MapperUtil()


def pad(res: str):
    # pad a string to be divisible by 4
    ilen = len(res)/4

    if not ilen.is_integer():
        n = ceil(ilen)*4 - len(res)

        res += '=' * n

    return res


def ceil(n: float):
    x = round(n)
    return x+1 if x < n else x
