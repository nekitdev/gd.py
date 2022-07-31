from gd.constants import EMPTY
from gd.string_constants import COMMA, MAPS, NEW_LINE, PIPE, STAR, TICK, UNDER, WRAP

wrap = WRAP.format
tick = TICK.format
maps = MAPS.format

concat_comma = COMMA.join
concat_empty = EMPTY.join
concat_new_line = NEW_LINE.join
concat_pipe = PIPE.join
concat_under = UNDER.join


def clear_whitespace(string: str) -> str:
    return concat_empty(string.split())


def password_str(password: str) -> str:
    return STAR * len(password)


def password_repr(password: str) -> str:
    return repr(password_str(password))


case_fold = str.casefold
