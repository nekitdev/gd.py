try:
    from aiohttp_apispec import docs, request_schema, setup_aiohttp_apispec  # type: ignore
    from marshmallow import Schema, fields  # type: ignore

except ImportError as error:
    raise ImportError("Can not define REST API.") from error

from aiohttp import web

import gd

web.run_app_async = web._run_app  # type: ignore  # idk why they made it internal

__all__ = (
    "Schema",
    "app",
    "client",
    "docs",
    "fields",
    "request_schema",
    "run_async",
    "run_sync",
    "web",
)

client = gd.Client()

routes = web.RouteTableDef()

app = web.Application()

setup_aiohttp_apispec(
    app=app,
    title="Documentation for gd.py API",
    version=str(gd.version_info),
    url="/api/docs/swagger.json",
    swagger_path="/api/docs",
)


def prepare_app() -> None:
    app.add_routes(routes)


def run_sync(**kwargs) -> None:
    prepare_app()

    web.run_app(app, **kwargs)


async def run_async(**kwargs) -> None:
    prepare_app()

    await web.run_app_async(app, **kwargs)  # type: ignore
