from ..errors import BadArgument

__all__ = ('convert_to_bool',)


def convert_to_bool(argument: str) -> bool:
    lower = argument.lower()

    if lower in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
        return True

    elif lower in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
        return False

    else:
        raise BadArgument('{} is not a recognised boolean option'.format(lower))
