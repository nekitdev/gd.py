.. currentmodule:: gd

0.8.2 - What's new?
=======================

0.8.0 is indeed a big update, which is as well breaking.
That means all versions below are not compatible with the
newest ones, and vice-versa. We hope that this was the last
update of that kind, however, with the new Geometry Dash versions,
gd.py updates may become breaking.

1. Why breaking?
----------------

Well, the problem is that in 0.7.1 and lower gd.py was using
globalised ``ctx`` object, which made most of aspects that require
logged in clients much more easy; but it has created one problem:
the multilogins were restricted.

2. Our decisions
----------------

We decided to rewrite the library and pass :class:`.Client` objects
where they are required.

3. Actually new things
----------------------

We added several cool functions, such as :meth:`.Client.get_messages`,
:meth:`.Level.get_comments`, :meth:`.Level.comment`, and some additional
changes were made as well.

- NeKitDS
