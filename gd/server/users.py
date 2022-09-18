from fastapi.responses import FileResponse

from gd.async_utils import run_blocking
from gd.server.core import app, client
from gd.server.icons import ICONS_PATH

SEARCH_USER_ICONS = "/search/user/{query}/icons"

QUERY = "query"

SEARCH_USER_NAME = "search_{}.png"


@app.get(SEARCH_USER_ICONS)
async def search_user_icons(query: str) -> FileResponse:
    path = ICONS_PATH / SEARCH_USER_NAME.format(query)

    user = await client.search_user(query)

    image = await user.generate_full_async()

    await run_blocking(image.save, path)

    return FileResponse(path)


GET_USER_ICONS = "/v1/users/{account_id}/icons"

ACCOUNT_ID = "account_id"

GET_USER_NAME = "get_{}.png"


@app.get(GET_USER_ICONS)
async def get_user_icons(account_id: int) -> FileResponse:
    path = ICONS_PATH / GET_USER_NAME.format(account_id)

    user = await client.get_user(account_id)

    image = await user.generate_full_async()

    await run_blocking(image.save, path)

    return FileResponse(path)
