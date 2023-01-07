from fastapi import FastAPI

from gd.client import Client
from gd.server.constants import NAME, V1, VERSION_1
from gd.server.tokens import ServerToken, ServerTokens

__all__ = ("client", "tokens", "app", "v1")

client = Client()

tokens = ServerTokens(ServerToken)

app = FastAPI(openapi_url=None, redoc_url=None)

v1 = FastAPI(title=NAME, version=VERSION_1)

app.mount(V1, v1)
