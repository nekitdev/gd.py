from fastapi import FastAPI

from gd.client import Client

__all__ = ("app", "client")

TITLE = "API Documentation"
VERSION = "0.1.0"
INFO_PATH = "/info.json"

app = FastAPI(title=TITLE, version=VERSION, openapi_url=INFO_PATH)

client = Client()
