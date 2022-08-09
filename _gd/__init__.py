try:
    from _gd._gd import cyclic_xor, xor  # type: ignore

except ImportError:
    pass

__all__ = ("cyclic_xor", "xor")
