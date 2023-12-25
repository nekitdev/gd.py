from typing import Union

from typing_extensions import TypedDict as Data
from yarl import URL

__all__ = ("Data", "AnyString", "IntString", "URLString")

AnyString = Union[str, bytes]
IntString = Union[int, str]
URLString = Union[URL, str]
