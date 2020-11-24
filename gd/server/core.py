from aiohttp_apispec import setup_aiohttp_apispec  # type: ignore
from aiohttp_remotes import ForwardedRelaxed, XForwardedRelaxed, setup as setup_aiohttp_remotes
from aiohttp import web

from gd.typing import Iterable, Optional, Protocol
import gd

__all__ = (
    "create_app",
    "create_app_sync",
    "routes",
    "run_app",
    "run_app_sync",
    "run",
    "run_sync",
    "web",
)


class Tool(Protocol):
    async def setup(self, app: web.Application) -> None:
        ...


DEFAULT_TOOLS: Iterable[Tool] = (ForwardedRelaxed(), XForwardedRelaxed())

run_app = web._run_app  # type: ignore  # idk why they made it internal
run_app_sync = web.run_app

routes = web.RouteTableDef()


async def create_app(
    *,
    client: Optional[gd.Client] = None,
    docs_title: str = "Documentation for GD API",
    docs_version: str = str(gd.version_info),
    docs_json_url: str = "/api/docs/swagger.json",
    docs_url: str = "/api/docs",
    tools: Iterable[Tool] = DEFAULT_TOOLS,
    **app_kwargs,
) -> web.Application:
    app = web.Application(**app_kwargs)

    setup_aiohttp_apispec(
        app=app, title=docs_title, version=docs_version, url=docs_json_url, swagger_path=docs_url
    )

    await setup_aiohttp_remotes(app, *tools)

    if client is None:
        client = gd.Client()

    app.client = client

    app.add_routes(routes)

    return app


def create_app_sync(
    *,
    client: Optional[gd.Client] = None,
    docs_title: str = "Documentation for GD API",
    docs_version: str = str(gd.version_info),
    docs_json_url: str = "/api/docs/swagger.json",
    docs_url: str = "/api/docs",
    tools: Iterable[Tool] = DEFAULT_TOOLS,
    **app_kwargs,
) -> web.Application:
    return gd.utils.acquire_loop().run_until_complete(
        create_app(
            client=client,
            docs_title=docs_title,
            docs_version=docs_version,
            docs_json_url=docs_json_url,
            docs_url=docs_url,
            tools=tools,
            **app_kwargs,
        )
    )


async def run(**run_kwargs) -> None:
    await run_app(await create_app(), **run_kwargs)


def run_sync(**run_kwargs) -> None:
    run_app_sync(create_app_sync(), **run_kwargs)
