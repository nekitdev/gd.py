from aiohttp.web import FileResponse, Request

from gd.client import Client
from gd.server.constants import CLIENT
from gd.server.handler import request_handler
from gd.server.icons import ICONS_PATH
from gd.server.routes import get

SEARCH_USER_ICONS = "/search/user/{query}/icons"

QUERY = "query"

SEARCH_USER_NAME = "search.{}.png"


@get(SEARCH_USER_ICONS, version=1)
@request_handler()
async def search_user_icons(request: Request) -> FileResponse:
    query = request.match_info[QUERY]

    path = ICONS_PATH / SEARCH_USER_NAME.format(query)

    client: Client = request.app[CLIENT]

    user = await client.search_user(query)

    image = await user.generate_full_async()

    image.save(path)

    return FileResponse(path)


GET_USER_ICONS = "/users/{account_id}/icons"

ACCOUNT_ID = "account_id"

GET_USER_NAME = "get.{}.png"


@get(GET_USER_ICONS, version=1)
@request_handler()
async def get_user_icons(request: Request) -> FileResponse:
    account_id = int(request.match_info[ACCOUNT_ID])

    path = ICONS_PATH / SEARCH_USER_NAME.format(account_id)

    client: Client = request.app[CLIENT]

    user = await client.get_user(account_id)

    image = await user.generate_full_async()

    image.save(path)

    return FileResponse(path)
