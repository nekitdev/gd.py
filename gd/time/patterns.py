from re import VERBOSE
from re import compile as re_compile

from gd.strings.concatenation import concat_pipe
from gd.time.constants import AGO, IN, NAME_TO_MILLISECONDS, NOW, S_LITERAL, SEPARATOR

DIGIT = r"[0-9]"

FUTURE = "future"
PAST = "past"

DURATIONS = "durations"
DURATION = "duration"

NAME = "name"

NAMES = concat_pipe(NAME_TO_MILLISECONDS)

HUMAN_DURATION_PATTERN = rf"""
    (?P<{DURATION}>{DIGIT}+)
    (?P<{NAME}>{NAMES}){S_LITERAL}?
"""

HUMAN_DURATION = re_compile(HUMAN_DURATION_PATTERN, VERBOSE)

# NOTE: the whitespace is removed before the matching

HUMAN_PATTERN = rf"""
    ^
    (?P<{NOW}>{NOW})
    |
    (?:
        (?P<{FUTURE}>{IN})?
        (?P<{DURATIONS}>
            (?:
                {HUMAN_DURATION_PATTERN}
                (?:{SEPARATOR})?
            )*
        )
        (?P<{PAST}>{AGO})?
    )
    $
"""

HUMAN = re_compile(HUMAN_PATTERN, VERBOSE)
