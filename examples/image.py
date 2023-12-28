"""Generating icons."""

from entrypoint import entrypoint

import gd
from gd.asyncio import run_blocking
from gd.queries import query

client = gd.Client()  # initialize the client

PROMPT = "name: "

NOT_FOUND = "user `{name}` not found"
not_found = NOT_FOUND.format

COSMETICS_NOT_FOUND = "user `{user.name}` cosmetics not found"
cosmetics_not_found = COSMETICS_NOT_FOUND.format

IMAGE_NAME = "{user.name}.png"
image_name = IMAGE_NAME.format


async def async_main() -> None:
    name = input(PROMPT)

    try:
        user = await client.search_user(query(name))

    except gd.MissingAccess:
        print(not_found(name=name))

    else:
        cosmetics = user.cosmetics

        if cosmetics is None:
            print(cosmetics_not_found(user=user))

        else:
            image = await cosmetics.generate_full_async()

            await run_blocking(image.save, image_name(user=user))


@entrypoint(__name__)
def main() -> None:
    client.run(async_main())
