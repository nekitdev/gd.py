from gd.strings.constants import STAR


def password_str(password: str) -> str:
    return STAR * len(password)


def password_repr(password: str) -> str:
    return repr(password_str(password))
