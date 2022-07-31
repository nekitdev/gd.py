"""Example of sending a message to a user.
Author: nekitdev.
"""

import random  # for fun

import gd

NO = {"n", "no"}  # items to recognize as *no*

client = gd.Client()  # initialize client


# one function to make things simplier
async def main() -> None:
    # login
    username, password = (
        input("Please enter your GD username: "),
        input("Enter corresponding password: "),
    )

    await client.login(username, password)

    # get all friends...
    friends = await client.get_friends().list()

    if not friends:
        print("Oh... Seems like you have no friends in GD...")

    # choose one target
    target = random.choice(friends)

    if input(f"Do you want to send a message to {target}? (y/n): ").casfold() in NO:
        return

    # send our message to them
    try:
        await target.send(subject="Hello!", body="This is a message sent using gd.py library!")

        # print that message was successfully sent
        print(f"Successfully sent a message to {target}!")

    # check if an error occured
    except gd.ClientException:  # if the user has their messages closed or other error occured
        print(f"Failed to send a message to {target}...")


# run the program
client.run(main())
