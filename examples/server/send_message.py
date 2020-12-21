"""Example of sending a message to a user.
Author: nekitdev.
"""

import random  # for fun

import gd

client = gd.Client()  # initialize client


# a coro to make things simplier
async def coro():
    # login
    username, password = (
        input("Please enter your GD username: "),
        input("Enter corresponding password: "),
    )

    await client.login(user=username, password=password)

    # get all friends...
    friends = await client.get_friends()

    if not friends:
        print("Oh... Seems like you have no friends in GD...")

    # choose one target
    target = random.choice(friends)

    if input(f"Do you want to send a message to {target}? (y/n): ").lower() in {
        "n",
        "no",
    }:
        return

    # send a message to them
    try:
        await target.send(subject="Hello!", body="This is a message sent using gd.py library!")

        # print that message was successfully sent
        print(f"Successfully sent a message to {target}!")

    # check if an error occured
    except gd.ClientException:  # if a user has their messages closed or other error occured
        print(f"Failed to send a message to {target}...")


# run a program
client.run(coro())
