from typing import Type, TypeVar

from attrs import field, frozen
from cattrs import Converter
from cattrs.gen import AttributeOverride, make_dict_unstructure_fn, override
from typing_aliases import AnyType, StringDict
from yarl import URL

__all__ = (
    "CONVERTER",
    "register_unstructure_hook",
    "register_unstructure_hook_omit_client",
)

CONVERTER = Converter(forbid_extra_keys=True)


def dump_url(url: URL) -> str:
    return url.human_repr()


def parse_url_ignore_type(string: str, type: Type[URL]) -> URL:
    return URL(string)


CONVERTER.register_unstructure_hook(URL, dump_url)
CONVERTER.register_structure_hook(URL, parse_url_ignore_type)


AttributeOverrides = StringDict[AttributeOverride]

T = TypeVar("T", bound=AnyType)


@frozen()
class RegisterUnstructureHook:
    overrides: AttributeOverrides = field(factory=dict, repr=False)

    def __call__(self, type: T) -> T:
        CONVERTER.register_unstructure_hook(
            type, make_dict_unstructure_fn(type, CONVERTER, **self.overrides)  # type: ignore
        )

        return type


def register_unstructure_hook(**overrides: AttributeOverride) -> RegisterUnstructureHook:
    return RegisterUnstructureHook(overrides)


register_unstructure_hook_omit_client = register_unstructure_hook(
    client_unchecked=override(omit=True)
)
