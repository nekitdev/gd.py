.. currentmodule:: gd

0.8.(0/1) - What's new?
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

3. Side notes
-------------

Many functions were adapted to the new client-passing paradigm.

3.1 Fixes
---------

0.8.1 - Fixed :meth:`.Client.update_profile` method to make it work as expected.
Sorry for inconveniece, updating to 0.8.1 and higher is recommended.

4. Additional changes
---------------------

gd.py has got somewhat useful console implementation:

.. code-block:: sh

    # show help
    python -m gd --help

    # show versions
    python -m gd --version

    # show docs link
    python -m gd --docs
