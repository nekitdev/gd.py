"""An example that shows user searching.
Author: nekitdev
"""

from entrypoint import entrypoint

import gd

client = gd.Client()  # initialize the client

PROMPT = "name: "

UNREGISTERED = "it seems `{user.name}` is not registered..."
REGISTERED = "`{user.name}` is registered (account ID: {user.account_id}, ID: {user.id})"
CAN_NOT_FIND = "can not find `{name}`"


async def async_main() -> None:
    name = input(PROMPT)

    try:
        user = await client.search_user(name, simple=True)

        print(
            REGISTERED.format(user=user) if user.is_registered() else UNREGISTERED.format(user=user)
        )

    except gd.MissingAccess:  # can not find
        print(CAN_NOT_FIND.format(name=name))


@entrypoint(__name__)
def main() -> None:
    client.run(async_main())
