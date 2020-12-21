"""Simple example showing user searching.
Author: nekitdev
"""

import gd

client = gd.Client()


async def main():
    # get some input from user
    name = input("Enter your GD nickname: ")

    # look up and print IDs if found
    try:
        user = await client.search_user(name, simple=True)

        if not user.is_registered():
            print(f"Hey there, {user.name}! Seems like you are unregistered...".format(user))

        else:
            print(
                f"Hello, {user.name}! Your AccountID is {user.account_id} "
                f"and PlayerID is {user.id}."
            )

    # could not find
    except gd.MissingAccess:
        print(f"Sorry, could not find user with name {name}...")


# run a program
client.run(main())
