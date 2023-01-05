from pathlib import Path
from typing import Iterable, List

from fastapi import Depends
from fastapi.responses import FileResponse

from gd.async_utils import run_blocking
from gd.server.constants import CACHE, ICONS
from gd.server.core import client, v1
from gd.server.dependencies import pages_dependency
from gd.users import User, UserData

__all__ = ("get_user", "get_user_icons", "search_user", "search_user_icons", "search_users")

PATH = Path(CACHE) / ICONS

PATH.mkdir(parents=True, exist_ok=True)

NORMAL_ICONS = "{}.icons.png"
SEARCH_ICONS = "search.{}.icons.png"


@v1.get("/users/{account_id}", summary="Fetches the user by the account ID.")
async def get_user(account_id: int) -> UserData:
    user = await client.get_user(account_id)

    return user.to_json()


@v1.get("/users/{account_id}/icons", summary="Fetches the user icons by the account ID.")
async def get_user_icons(account_id: int) -> FileResponse:
    path = PATH / NORMAL_ICONS.format(account_id)

    if path.exists():
        return FileResponse(path)

    user = await client.get_user(account_id)

    image = await user.generate_full_async()

    await run_blocking(image.save, path)

    return FileResponse(path)


@v1.get("/search/user/{query}", summary="Searches for the user by the query.")
async def search_user(query: str) -> UserData:
    user = await client.search_user(query)

    return user.to_json()


@v1.get("/search/user/{query}/icons", summary="Searches for the user icons by the query.")
async def search_user_icons(query: str) -> FileResponse:
    path = PATH / SEARCH_ICONS.format(query)

    if path.exists():
        return FileResponse(path)

    user = await client.search_user(query)

    image = await user.generate_full_async()

    await run_blocking(image.save, path)

    return FileResponse(path)


def user_to_json(user: User) -> UserData:
    return user.to_json()


@v1.get("/search/users/{query}", summary="Searches for users by the query.")
async def search_users(query: str, pages: Iterable[int] = Depends(pages_dependency)) -> List[UserData]:
    return await client.search_users(query, pages=pages).map(user_to_json).list()
