"""Example that shows getting current daily/weekly levels.
Author: nekitdev.
"""

import gd

client = gd.Client()  # an entry point to gd API

# let's create one coroutine to use
# run() only once.


async def main():
    # getting daily...
    daily = await client.get_daily()

    # getting weekly...
    weekly = await client.get_weekly()

    # now let's print...
    print(f"Current daily: {daily}, weekly: {weekly}.")


# run a coroutine
client.run(main())
