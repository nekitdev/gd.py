from aiohttp_apispec import setup_aiohttp_apispec  # type: ignore
from aiohttp_remotes import setup as setup_aiohttp_remotes

import gd

from gd.server.common import ForwardedRelaxed, XForwardedRelaxed, web
from gd.server.middlewares import status_error_middleware
from gd.server.routes import routes
from gd.server.token import Token, TokenDatabase, ServerToken, ServerTokenDatabase
from gd.server.typing import Middleware
from gd.typing import Iterable, Optional, Protocol, Type

__all__ = (
    "Tool",
    "create_app",
    "create_app_sync",
    "create_gd_app",
    "create_gd_app_sync",
    "run_app",
    "run_app_sync",
    "run",
    "run_sync",
    "run_gd",
    "run_gd_sync",
    "web",
)


class Tool(Protocol):
    async def setup(self, app: web.Application) -> None:
        ...


DEFAULT_MIDDLEWARES: Iterable[Middleware] = (
    status_error_middleware(),
    web.normalize_path_middleware(append_slash=False, remove_slash=True),
)
DEFAULT_TOOLS: Iterable[Tool] = ()
DEFAULT_GD_TOOLS: Iterable[Tool] = (ForwardedRelaxed(), XForwardedRelaxed())

run_app = web._run_app  # type: ignore  # no idea why it was made internal
run_app_sync = web.run_app


async def create_app(
    *,
    docs_title: str = "API Documentation",
    docs_version: str = str(gd.version_info),
    docs_info_url: str = "/api/docs/info.json",
    docs_url: str = "/api/docs",
    middlewares: Iterable[Middleware] = DEFAULT_MIDDLEWARES,
    tools: Iterable[Tool] = DEFAULT_TOOLS,
    token_database: Type[TokenDatabase] = TokenDatabase,
    token: Type[Token] = Token,
    **app_kwargs,
) -> web.Application:
    app = web.Application(**app_kwargs)

    app.middlewares.extend(middlewares)

    setup_aiohttp_apispec(
        app=app, title=docs_title, version=docs_version, url=docs_info_url, swagger_path=docs_url
    )

    await setup_aiohttp_remotes(app, *tools)

    app.token_database = token_database(token)

    return app


def create_app_sync(
    *,
    docs_title: str = "API Documentation",
    docs_version: str = str(gd.version_info),
    docs_info_url: str = "/api/docs/info.json",
    docs_url: str = "/api/docs",
    middlewares: Iterable[Middleware] = DEFAULT_MIDDLEWARES,
    tools: Iterable[Tool] = DEFAULT_TOOLS,
    token_database: Type[TokenDatabase] = TokenDatabase,
    token: Type[Token] = Token,
    default: bool = False,
    **app_kwargs,
) -> web.Application:
    return gd.utils.get_not_running_loop().run_until_complete(
        create_app(
            docs_title=docs_title,
            docs_version=docs_version,
            docs_info_url=docs_info_url,
            docs_url=docs_url,
            middlewares=middlewares,
            tools=tools,
            token_database=token_database,
            token=token,
            default=default,
            **app_kwargs,
        )
    )


async def create_gd_app(
    *,
    client: Optional[gd.Client] = None,
    docs_title: str = "GD API Documentation",
    docs_version: str = str(gd.version_info),
    docs_info_url: str = "/api/docs/info.json",
    docs_url: str = "/api/docs",
    middlewares: Iterable[Middleware] = DEFAULT_MIDDLEWARES,
    tools: Iterable[Tool] = DEFAULT_GD_TOOLS,
    token_database: Type[ServerTokenDatabase] = ServerTokenDatabase,
    token: Type[ServerToken] = ServerToken,
    **app_kwargs,
) -> web.Application:
    app = await create_app(
        docs_title=docs_title,
        docs_version=docs_version,
        docs_info_url=docs_info_url,
        docs_url=docs_url,
        middlewares=middlewares,
        tools=tools,
        token_database=token_database,
        token=token,
        **app_kwargs,
    )

    if client is None:
        client = gd.Client()

    app.client = client

    app.add_routes(routes)

    return app


def create_gd_app_sync(
    *,
    client: Optional[gd.Client] = None,
    docs_title: str = "GD API Documentation",
    docs_version: str = str(gd.version_info),
    docs_info_url: str = "/api/docs/info.json",
    docs_url: str = "/api/docs",
    middlewares: Iterable[Middleware] = DEFAULT_MIDDLEWARES,
    tools: Iterable[Tool] = DEFAULT_GD_TOOLS,
    token_database: Type[ServerTokenDatabase] = ServerTokenDatabase,
    token: Type[ServerToken] = ServerToken,
    **app_kwargs,
) -> web.Application:
    return gd.utils.get_not_running_loop().run_until_complete(
        create_gd_app(
            client=client,
            docs_title=docs_title,
            docs_version=docs_version,
            docs_info_url=docs_info_url,
            docs_url=docs_url,
            middlewares=middlewares,
            tools=tools,
            token_database=token_database,
            token=token,
            **app_kwargs,
        )
    )


async def run(**run_kwargs) -> None:
    await run_app(await create_app(), **run_kwargs)


async def run_gd(**run_kwargs) -> None:
    await run_app(await create_gd_app(), **run_kwargs)


def run_sync(**run_kwargs) -> None:
    run_app_sync(create_app_sync(), **run_kwargs)


def run_gd_sync(**run_kwargs) -> None:
    run_app_sync(create_gd_app_sync(), **run_kwargs)
