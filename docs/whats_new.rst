.. currentmodule:: gd

[0.8.x | 0.9.x] - What's new?
=============================

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

0.8.2 - We added several cool functions, such as :meth:`.Client.get_messages`,
:meth:`.Level.get_comments`, :meth:`.Level.comment`, and some additional
changes were made as well.

0.8.3 - Fixed not removed server response printing. Sorry for inconvenience.

0.9.0a1 - Fixed a lot of things, added quite a decent amount as well. No details yet.

0.9.0a2 - Fixed stupid typos, everything should be fine now.

- NeKitDS
