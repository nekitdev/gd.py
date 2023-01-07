from cattrs import Converter

__all__ = ("CONVERTER",)

CONVERTER = Converter(forbid_extra_keys=True)
