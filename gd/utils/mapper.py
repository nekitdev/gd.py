from .wrap_tools import convert_to_type

__all__ = ('mapper', 'MapperUtil', 'pad', 'ceil')


class MapperUtil:
    @staticmethod
    def map(item, try_convert: bool = True):
        convert = lambda obj: convert_to_type(obj, int)
        mapping = zip(item[::2], item[1::2])

        if try_convert:
            res = {convert(key): convert(value) for key, value in mapping}

        else:
            res = {convert(key): value for key, value in mapping}

        return res

    @staticmethod
    def normalize(item):
        res = str(item).replace('-', '+').replace('_', '/')
        return pad(res)

    @staticmethod
    def prepare_sending(item):
        res = str(item).replace('+', '-').replace('/', '_')
        return pad(res)

mapper = MapperUtil()


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
