try:
    import gc
except ImportError:
    pass

__all__ = ('get_instances_of', 'find_objects')

from ..typing import Any, Callable, List, Optional, Type


def get_instances_of(obj_class: Type[Any] = object) -> List[Any]:
    def predicate(obj: Any) -> bool:
        return isinstance(obj, obj_class)

    return find_objects(predicate)


def find_objects(predicate: Optional[Callable[[Any], bool]] = None) -> List[Any]:
    objects = gc.get_objects()

    if predicate is None:
        return objects

    return list(filter(predicate, objects))
