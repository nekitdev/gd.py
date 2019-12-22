from typing import Union, Sequence

from .enums import *
from .struct import *

from ..abstractentity import AbstractEntity
from ..errors import EditorError
from ..utils.wrap_tools import make_repr

__all__ = ('Editor', 'get_length_from_x')

speed_map = {}

for s in ('slow', 'normal', 'fast', 'faster', 'fastest'):
    a, b, c = (
        SpeedMagic[s.upper()],
        Speed[s.upper()],
        PortalType[s.title()+'Speed']
    )
    speed_map.update({b.value: a.value, c.value: a.value})

speeds = {enum.value for enum in PortalType if 'Speed' in enum.name}


def get_length_from_x(dx: float, start_speed: Speed, portals: Sequence[Object]) -> float:
    speed = speed_map.get(start_speed.value)

    if not portals:
        return dx / speed

    last_x = 0.0
    total = 0.0

    for portal in portals:
        if dx <= last_x:
            break

        x = portal.x

        current = x - last_x

        total += current / speed

        speed = speed_map.get(portal.id, 1)

        last_x = x

    return (dx - last_x) / speed + total


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

    def get_speed_portals(self):
        def f(obj):
            return obj.id in speeds and obj.is_checked
        def g(obj):
            return obj.x

        return sorted(filter(f, self.objects), key=g)

    def get_x_length(self):
        return max((obj.x for obj in self.objects), default=0)

    def get_speed(self):
        return self.header.speed or Speed(0)

    def get_length(self):
        x, speed, portals = (
            self.get_x_length(),
            self.get_speed(),
            self.get_speed_portals()
        )
        return get_length_from_x(x, speed, portals)

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
