.. currentmodule:: gd

Comments, Friend Requests and Messages
======================================

gd.py implements reading, sending and interacting with comments, friend requests and messages::

    client = gd.Client()

    # we can only read comments if we are not logged in.
    await client.login('username', 'password')

    nekit = await client.search_user('NeKitDS')
    # <gd.User account_id=5509312 id=17876467 name='NeKitDS' ...>

    for comment in await nekit.get_comments():
        print(comment.body)

    # find some featured level by user
    levels = await nekit.get_levels()

    level = gd.utils.find(lambda level: level.is_featured(), levels)

    # if found, print comments and post a comment
    if level is not None:
        for comment in level.get_comments():
            print(comment)

        await level.comment('gd.py testing')

    # print some messages
    for message in await client.get_messages():
        print(message.author.name, message.subject)

    # send a friend request
    await nekit.send_friend_request('<sent-from-gd.py>')

    # post a comment
    await client.post_comment('This comment is posted using gd.py')

Comment
-------

.. autoclass:: Comment
    :members:

Friend Request
--------------

.. autoclass:: FriendRequest
    :members:

Message
-------

.. autoclass:: Message
    :members:
