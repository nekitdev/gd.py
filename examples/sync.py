"""Example that shows running asynchronous functions synchronously.
Author: nekitdev.
"""

import gd

client = gd.Client()  # create our client

robtop = client.run(client.get_user(71))  # you can use client.run(...)

print(f"Using client.run(...): {robtop}")

robtop = client.sync_search_user("RobTop")  # type: ignore  # or client.sync_<name>(...)

print(f"Using client.sync_<name>(...): {robtop}")

robtop = robtop.sync_get_user()  # type: ignore  # or even this!

print(f"Using AbstractEntity.sync_<name>(...): {robtop}")
