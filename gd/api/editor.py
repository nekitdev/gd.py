from typing import Union, Sequence

from .struct import *

from ..abstractentity import AbstractEntity
from ..errors import EditorError
from ..utils.wrap_tools import make_repr

__all__ = ('Editor',)


class Editor:
    """Editor interface of gd.py.

    Editor can be created either by hand, from decoded level's data, or taken from a level itself.
    """
    def __init__(self, header: Header = None, *objects):
        self.header = header or Header()
        self.objects = list(objects)

    @classmethod
    def from_string(cls, data: Union[bytes, str]):
        if isinstance(data, bytes):
            try:
                data = data.decode()

            except UnicodeDecodeError:
                raise EditorError('Invalid level data recieved.') from None

        info, *objects = data.split(';')

        # remove last object if none
        try:
            last = objects.pop()
            if last:
               objects.append(last)
        except IndexError:
            pass

        header = Header.from_string(info)
        objects = list(map(Object.from_string, objects))

        return cls(header, *objects)

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
        """Add objects to ``self.objects``."""
        objects = list(filter(lambda obj: isinstance(obj, Object), objects))
        self.objects.extend(objects)

    def copy_objects(self):
        """List[:class:`.api.Object`]: Copy objects of ``self``.
        Note: copies, not references are returned!
        """
        return [obj.copy() for obj in self.objects]

    def map(self, function):
        """:class:`map`: Same as calling ``map`` on ``self.objects``."""
        return map(function, self.objects)

    def filter(self, function):
        """:class:`filter`: Same as calling ``filter`` on ``self.objects``."""
        return filter(function, self.objects)

    def dump_to_level(self, level, append_sc: bool = True):
        """Dump ``self`` to a ``level`` object."""
        level.options['data'] = self.dump(append_sc=append_sc)

    def dump(self, append_sc: bool = True):
        """Dump all objects and header into a level data string."""
        seq = [self.header.dump(), *(obj.dump() for obj in self.objects)]

        if append_sc:
            seq.append(str())

        data = ';'.join(map(str, seq))
        return data
