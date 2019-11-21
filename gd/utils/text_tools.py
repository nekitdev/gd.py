from typing import Union

__all__ = ('object_split',)


def object_split(string: Union[bytes, str]):
    sc = ';' if isinstance(string, str) else b';'

    final = string.split(sc)
    final.pop(0)

    if string.endswith(sc):
        final.pop()

    return final
