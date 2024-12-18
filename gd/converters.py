from typing import Type, TypeVar

from attrs import field, frozen
from cattrs import Converter
from cattrs.gen import AttributeOverride  # type: ignore[attr-defined]
from cattrs.gen import make_dict_unstructure_fn, override
from typing_aliases import AnyType, StringDict
from yarl import URL

__all__ = (
    "CONVERTER",
    "register_unstructure_hook",
    "register_unstructure_hook_omit_client",
)

CONVERTER = Converter(forbid_extra_keys=True)

U = TypeVar("U", bound=URL)


def unstructure_url(url: URL) -> str:
    return url.human_repr()


def structure_url(string: str, url_type: Type[U]) -> U:  # since URLs can not be derived
    return url_type(string)


CONVERTER.register_unstructure_hook(URL, unstructure_url)
CONVERTER.register_structure_hook(URL, structure_url)


AttributeOverrides = StringDict[AttributeOverride]

T = TypeVar("T", bound=AnyType)


@frozen()
class RegisterUnstructureHook:
    overrides: AttributeOverrides = field(factory=dict, repr=False)

    def __call__(self, type: T) -> T:
        CONVERTER.register_unstructure_hook(
            type,
            make_dict_unstructure_fn(type, CONVERTER, **self.overrides),  # type: ignore
        )

        return type


def register_unstructure_hook(
    **overrides: AttributeOverride,
) -> RegisterUnstructureHook:
    return RegisterUnstructureHook(overrides)


register_unstructure_hook_omit_client = register_unstructure_hook(client=override(omit=True))
