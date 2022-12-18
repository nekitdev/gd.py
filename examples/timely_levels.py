"""An example that shows fetching current timely levels.
Author: nekitdev.
"""

from entrypoint import entrypoint

import gd

client = gd.Client()  # initialize the client

DAILY = "daily: `{daily.name}` by `{daily.creator.name}` (ID: {daily.id})"
WEEKLY = "weekly: `{weekly.name}` by `{weekly.creator.name}` (ID: {weekly.id})"


async def async_main() -> None:
    print(DAILY.format(daily=await client.get_daily()))  # fetching daily...
    print(WEEKLY.format(weekly=await client.get_weekly()))  # fetching weekly...


@entrypoint(__name__)
def main() -> None:
    client.run(async_main())
