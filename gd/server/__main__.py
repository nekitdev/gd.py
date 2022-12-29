from entrypoint import entrypoint

from gd.server.main import server

entrypoint(__name__).call(server)
