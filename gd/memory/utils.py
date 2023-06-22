from iters.utils import unary_tuple

__all__ = unary_tuple("next_power_of_two")


def next_power_of_two(value: int) -> int:
    """Returns the next power of two for the given `value`.

    Arguments:
        value: The value to get the next power of two for.

    Returns:
        The next power of two.
    """
    return 1 << value.bit_length()
