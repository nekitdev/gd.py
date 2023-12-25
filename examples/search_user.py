"""Searching for users."""

from entrypoint import entrypoint

import gd

client = gd.Client()  # initialize the client

PROMPT = "name: "

UNREGISTERED = "it seems `{user.name}` is not registered..."
unregistered = UNREGISTERED.format

REGISTERED = "`{user.name}` is registered (account ID: `{user.account_id}`, ID: `{user.id}`)"
registered = REGISTERED.format

NOT_FOUND = "user `{name}` not found"
not_found = NOT_FOUND.format


async def async_main() -> None:
    name = input(PROMPT)

    try:
        user = await client.search_user(name, simple=True)

    except gd.MissingAccess:
        print(not_found(name=name))

    else:
        print(registered(user=user) if user.is_registered() else unregistered(user=user))


@entrypoint(__name__)
def main() -> None:
    client.run(async_main())
