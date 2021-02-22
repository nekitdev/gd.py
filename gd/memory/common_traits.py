from gd.memory.traits import Read, Write, Sized
from gd.typing import TypeVar

__all__ = ("ReadSized", "ReadWriteSized", "WriteSized")

T = TypeVar("T")


class ReadSized(Read[T], Sized):
    pass


class WriteSized(Write[T], Sized):
    pass


class ReadWriteSized(Read[T], Write[T], Sized):
    pass
