from typing import Iterable, Optional

from gd.constants import DEFAULT_PAGES
from gd.server.utils import parse_pages

__all__ = ("pages_dependency",)


def pages_dependency(pages: Optional[str] = None) -> Iterable[int]:
    if pages is None:
        return DEFAULT_PAGES

    return parse_pages(pages)
