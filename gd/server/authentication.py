from fastapi import Depends

from gd.server.core import tokens, v1
from gd.server.dependencies import token_dependency
from gd.server.tokens import ServerToken, TokenData


@v1.post("/login", summary="Performs the login and returns the token for future use.")
async def login(name: str, password: str) -> TokenData:
    token = tokens.find(name, password)

    if token is None:
        token = await tokens.register(name, password)

    return TokenData(token=token.value)


@v1.post("/logout", summary="Performs the logout.")
async def logout(token: ServerToken = Depends(token_dependency)) -> None:
    tokens.remove(token)
