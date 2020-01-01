from .wrap_tools import convert_to_type

__all__ = ('mapper', 'MapperUtil', 'pad')


def convert(obj):
    return convert_to_type(obj, int)


class MapperUtil:
    @staticmethod
    def map(item, try_convert: bool = True):
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
    while len(res) % 4:
        res += '='

    return res
