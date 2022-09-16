from typing import Iterable, Optional, Type, TypeVar

from aiohttp.web import Application, normalize_path_middleware, run_app
from aiohttp_apispec import docs, setup_aiohttp_apispec  # type: ignore
from aiohttp_remotes import setup as setup_aiohttp_remotes

from gd.client import Client
from gd.server.constants import CLIENT, DOCS, INFO, TITLE, TOKENS
from gd.server.routes import ROUTES
from gd.server.tokens import AnyTokens, ServerToken, ServerTokens, Token, Tokens
from gd.server.typing import StreamMiddleware, Tool
from gd.version import version_info

__all__ = ("docs", "setup_app", "setup_gd_app", "run_app")

VERSION = str(version_info)

DEFAULT_MIDDLEWARES: Iterable[StreamMiddleware] = (
    normalize_path_middleware(append_slash=False, remove_slash=True),
)

DEFAULT_TOOLS: Iterable[Tool] = ()

STATIC_PATH = "/swagger"

A = TypeVar("A", bound=Application)


async def setup_app(
    app: A,
    *,
    title: str = TITLE,
    version: str = VERSION,
    info: str = INFO,
    docs: str = DOCS,
    static_path: str = STATIC_PATH,
    middlewares: Iterable[StreamMiddleware] = DEFAULT_MIDDLEWARES,
    tools: Iterable[Tool] = DEFAULT_TOOLS,
    tokens_type: Type[AnyTokens] = Tokens,
    token_type: Type[Token] = Token,
) -> A:
    app.middlewares.extend(middlewares)

    setup_aiohttp_apispec(
        app=app, title=title, version=version, url=info, swagger_path=docs, static_path=static_path
    )

    await setup_aiohttp_remotes(app, *tools)

    app[TOKENS] = tokens_type(token_type)

    return app


async def setup_gd_app(
    app: A,
    *,
    client: Optional[Client] = None,
    title: str = TITLE,
    version: str = VERSION,
    info: str = INFO,
    docs: str = DOCS,
    static_path: str = STATIC_PATH,
    middlewares: Iterable[StreamMiddleware] = DEFAULT_MIDDLEWARES,
    tools: Iterable[Tool] = DEFAULT_TOOLS,
    tokens_type: Type[ServerTokens] = ServerTokens,
    token_type: Type[ServerToken] = ServerToken,
) -> A:
    await setup_app(
        app,
        title=title,
        version=version,
        info=info,
        docs=docs,
        static_path=static_path,
        middlewares=middlewares,
        tools=tools,
        tokens_type=tokens_type,
        token_type=token_type,
    )

    if client is None:
        client = Client()

    app[CLIENT] = client

    app.add_routes(ROUTES)

    return app
