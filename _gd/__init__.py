try:
    from _gd._gd import Reader, Writer  # type: ignore

except ImportError:
    pass

__all__ = ("Reader", "Writer")
