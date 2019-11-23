from typing import Union, Sequence

from .object import Object

from ..abstractentity import AbstractEntity
from ..utils.wrap_tools import find_subclass, make_repr

__all__ = ('Editor',)

Level = find_subclass('Level', AbstractEntity)


class Editor:
    def __init__(self, data_or_level: Union[bytes, str, Level] = ''):
        data = data_or_level

        if isinstance(data_or_level, Level):
            data = data_or_level.data

        if isinstance(data, bytes):
            try:
                data = data.decode()

            except UnicodeDecodeError:
                raise ValueError('Invalid level data recieved.') from None

        info, *objects = data.split(';')

        # remove last object if none
        try:
            last = objects.pop()
            if last:
               objects.append(last)
        except IndexError:
            pass

        # actually convert
        self.info = info  # TODO: conversion
        self.objects = list(map(Object.from_string, objects))

    def __repr__(self):
        info = {
            'len': len(self.objects),
            'objects': repr('...')
        }
        return make_repr(self, info)

    def __iter__(self):
        return iter(self.objects)

    def __len__(self):
        return len(self.objects)

    def add_objects(self, *objects: Sequence[Object]):
        objects = list(filter(lambda obj: isinstance(obj, Object), objects))
        self.objects.extend(objects)

    def dump(self, append_sc: bool = True):
        seq = [self.info, *(obj.dump() for obj in self.objects)]

        if append_sc:
            seq.append(str())

        data = ';'.join(map(str, seq))
        return data
