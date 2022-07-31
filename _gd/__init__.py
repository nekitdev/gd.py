try:
    from _gd._gd import cyclic_xor, xor

except ImportError:
    pass

__all__ = ("cyclic_xor", "xor")
