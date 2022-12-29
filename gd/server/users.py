from pathlib import Path

from fastapi.responses import FileResponse

from gd.async_utils import run_blocking
from gd.server.constants import CACHE, ICONS
from gd.server.core import client, v1
from gd.users import User, UserData

PATH = Path(CACHE) / ICONS

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


@v1.get("/users/search/{query}", summary="Searches for the user by the query.")
async def search_user(query: str) -> UserData:
    user = await client.search_user(query)

    return user.to_json()
