.. currentmodule:: gd

Comments, Friend Requests and Messages
======================================

gd.py implements reading, sending and interacting with comments, friend requests and messages::

    client = gd.Client()

    # we can only read comments if we are not logged in.
    await client.login("username", "password")

    nekit = await client.search_user("nekitdev")
    # <User name='nekitdev' id=17876467 account_id=5509312>

    async for comment in nekit.get_profile_comments():
        print(comment.body)

    # find some featured level by user
    level = await nekit.search_levels().find(lambda level: level.is_featured())

    # if found, print comments
    if level is not None:
        async for comment in level.get_comments():
            print(comment)

    # print some messages
    async for message in client.get_messages():
        print(message.author.name, message.subject)

    # send a friend request
    await nekit.send_friend_request("Sent from gd.py")

    # post a comment
    await client.post_comment("This comment is posted using gd.py")

Comment
-------

.. autoclass:: Comment
    :inherited-members:
    :members:

Friend Request
--------------

.. autoclass:: FriendRequest
    :inherited-members:
    :members:

Message
-------

.. autoclass:: Message
    :inherited-members:
    :members:
