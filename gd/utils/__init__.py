import asyncio

from ._async import *
from .enums import value_to_enum
from .search_utils import find, get
from .wrap_tools import *

def convert_to_type(obj: object, try_type: type, on_fail_type: type = None):
    """A function that tries to convert the given object to a provided type

    Parameters
    ----------
    obj: :class:`object`
        Any object to convert into given type.

    try_type: :class:`type`
        Type to convert an object to.

    on_fail_type: :class:`type`
        Type to convert an object on fail.
        If ``None`` or omitted, returns an ``obj``.
        On fail returns ``obj`` as well.

    Returns
    -------
    `Any`
        Object of given ``try_type``, on fail of type ``on_fail_type``, and
        ``obj`` if ``on_fail_type`` is ``None`` or failed to convert.
    """
    try:
        return try_type(obj)
    except Exception:  # failed to convert
        try:
            return on_fail_type(obj)
        except Exception:
            return obj
