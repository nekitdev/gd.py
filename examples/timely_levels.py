"""An example that shows fetching current timely levels.
Author: nekitdev.
"""

from entrypoint import entrypoint

import gd

client = gd.Client()  # initialize the client

DAILY_STRING = "daily: `{daily.name}` by `{daily.creator.name}` (ID: `{daily.id}`)"
daily_string = DAILY_STRING.format

WEEKLY_STRING = "weekly: `{weekly.name}` by `{weekly.creator.name}` (ID: `{weekly.id}`)"
weekly_string = WEEKLY_STRING.format

DAILY_NOT_FOUND = "`daily` not found"
WEEKLY_NOT_FOUND = "`weekly` not found"


async def async_main() -> None:
    try:
        daily = await client.get_daily()  # fetching daily...

    except gd.GDError:
        print(DAILY_NOT_FOUND)

        return

    try:
        weekly = await client.get_weekly()  # fetching weekly...

    except gd.GDError:
        print(WEEKLY_NOT_FOUND)

        return

    print(daily_string(daily=daily))
    print(weekly_string(weekly=weekly))


@entrypoint(__name__)
def main() -> None:
    client.run(async_main())
