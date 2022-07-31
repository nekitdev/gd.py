"""Example that shows getting current daily/weekly levels.
Author: nekitdev.
"""

import gd

client = gd.Client()  # an entry point to gd API

# let's create one coroutine to use
# run() only once.


async def main() -> None:
    # getting daily...
    daily = await client.get_daily()

    # getting weekly...
    weekly = await client.get_weekly()

    # now let us print...
    print(f"Current daily: {daily.name} (ID: {daily.id})")
    print(f"Current weekly: {weekly.name} (ID: {weekly.id})")


# run a coroutine
client.run(main())
