from pathlib import Path
from typing import Iterable, List

from fastapi import Depends
from fastapi.responses import FileResponse

from gd.asyncio import run_blocking
from gd.errors import InternalError
from gd.level import Level, LevelData
from gd.server.constants import CACHE, ICONS, ME
from gd.server.core import client, v1
from gd.server.dependencies import pages_dependency, token_dependency
from gd.server.tokens import ServerToken
from gd.users import User, UserData

__all__ = (
    "get_self",
    "get_self_icons",
    "get_self_levels",
    "get_user",
    "get_user_icons",
    "get_user_levels",
    "search_user",
    "search_user_icons",
    "search_user_levels",
    "search_users",
)

PATH = Path(CACHE) / ICONS

PATH.mkdir(parents=True, exist_ok=True)

NORMAL_ICONS = "{}.icons.png"
SEARCH_ICONS = "search.{}.icons.png"
SELF_ICONS = "me.{}.icon.png"


@v1.get(f"/users/{ME}", summary="Fetches the self user.")
async def get_self(token: ServerToken = Depends(token_dependency)) -> UserData:
    user = await token.client.user.get()

    return user.into_data()


@v1.get("/users/{account_id}", summary="Fetches the user by the account ID.")
async def get_user(account_id: int) -> UserData:
    user = await client.get_user(account_id)

    return user.into_data()


@v1.get(f"/users/{ME}/icons", summary="Fetches the self user icons.")
async def get_self_icons(token: ServerToken = Depends(token_dependency)) -> FileResponse:
    client = token.client

    path = PATH / NORMAL_ICONS.format(client.name)

    if path.exists():
        return FileResponse(path)

    user = await client.user.get()

    cosmetics = user.cosmetics

    if cosmetics is None:
        raise InternalError  # TODO: message?

    image = await cosmetics.generate_full_async()

    await run_blocking(image.save, path)

    return FileResponse(path)


@v1.get("/users/{account_id}/icons", summary="Fetches the user icons by the account ID.")
async def get_user_icons(account_id: int) -> FileResponse:
    path = PATH / NORMAL_ICONS.format(account_id)

    if path.exists():
        return FileResponse(path)

    user = await client.get_user(account_id)

    cosmetics = user.cosmetics

    if cosmetics is None:
        raise InternalError  # TODO: message?

    image = await cosmetics.generate_full_async()

    await run_blocking(image.save, path)

    return FileResponse(path)


def level_into_data(level: Level) -> LevelData:
    return level.into_data()


@v1.get(f"/users/{ME}/levels", summary="Fetches the self user levels.")
async def get_self_levels(
    pages: Iterable[int] = Depends(pages_dependency), token: ServerToken = Depends(token_dependency)
) -> List[LevelData]:
    return await token.client.user.get_levels(pages=pages).map(level_into_data).list()


@v1.get("/users/{account_id}/levels", summary="Fetches the user levels by the account ID.")
async def get_user_levels(
    account_id: int, pages: Iterable[int] = Depends(pages_dependency)
) -> List[LevelData]:
    user = await client.get_user(account_id)

    return await user.get_levels(pages=pages).map(level_into_data).list()


@v1.get("/search/user/{query}", summary="Searches for the user by the query.")
async def search_user(query: str) -> UserData:
    user = await client.search_user(query)

    return user.into_data()


@v1.get("/search/user/{query}/icons", summary="Searches for the user icons by the query.")
async def search_user_icons(query: str) -> FileResponse:
    path = PATH / SEARCH_ICONS.format(query)

    if path.exists():
        return FileResponse(path)

    user = await client.search_user(query)

    cosmetics = user.cosmetics

    if cosmetics is None:
        raise InternalError  # TODO: message?

    image = await cosmetics.generate_full_async()

    await run_blocking(image.save, path)

    return FileResponse(path)


@v1.get("/search/user/{query}/levels", summary="Searches for the user levels by the query.")
async def search_user_levels(
    query: str, pages: Iterable[int] = Depends(pages_dependency)
) -> List[LevelData]:
    user = await client.search_user(query)

    return await user.get_levels(pages=pages).map(level_into_data).list()


def user_into_data(user: User) -> UserData:
    return user.into_data()


@v1.get("/search/users/{query}", summary="Searches for users by the query.")
async def search_users(
    query: str, pages: Iterable[int] = Depends(pages_dependency)
) -> List[UserData]:
    return await client.search_users(query, pages=pages).map(user_into_data).list()
