"""Searching for users."""

from entrypoint import entrypoint

from gd.clients import Client
from gd.errors import MissingAccess
from gd.primitives.queries.queries import query

client = Client()  # initialize the client

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
        user = await client.search_user(query(name), simple=True)

    except MissingAccess:
        print(not_found(name=name))

    else:
        print(registered(user=user) if user.is_registered() else unregistered(user=user))


@entrypoint(__name__)
def main() -> None:
    try:
        client.run(async_main())

    except KeyboardInterrupt:
        pass
