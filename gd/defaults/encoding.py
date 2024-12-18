from os import environ as environment

__all__ = ("DEFAULT_ENCODING", "DEFAULT_ERRORS")

DEFAULT_ENCODING = "utf-8"
"""The default encoding to use."""

STRICT_ERRORS = "strict"
"""The strict errors strategy."""

GD_ENCODING_ERRORS = "GD_ENCODING_ERRORS"
"""The environment variable of the default errors strategy to use."""

DEFAULT_ERRORS = environment.get(GD_ENCODING_ERRORS, STRICT_ERRORS)
"""The default errors strategy to use."""
