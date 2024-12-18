from gd.strings.constants import ZERO_PADDING

zero_padding = ZERO_PADDING.format


def zero_pad(align: int, string: str) -> str:
    return zero_padding(string=string, align=align)
