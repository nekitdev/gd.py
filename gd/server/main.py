import click
import uvicorn

from gd.server.constants import DEFAULT_HOST, DEFAULT_PORT
from gd.server.core import app

__all__ = ("server",)


@click.option("--host", "-h", default=DEFAULT_HOST, type=str)
@click.option("--port", "-p", default=DEFAULT_PORT, type=int)
@click.command()
def server(host: str, port: int) -> None:
    uvicorn.run(app, host=host, port=port)
