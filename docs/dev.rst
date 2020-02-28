.. _development_api:

.. currentmodule:: gd

Development API Reference
=========================

The following section outlines the API of gd.py for library developers.

.. note::

    This section is only for gd.py developers, nothing interesting and
    useful for basic users here.

HTTP Requests Module
--------------------

.. autoclass:: HTTPClient
    :members:

.. autoclass:: GDSession

.. note:: See source of the session for more information.

Parameters Creating
-------------------

.. autoclass:: Parameters
    :members:

Ciphers and Coders
------------------

.. currentmodule:: gd.utils.crypto.xor_cipher

.. autoclass:: XORCipher
    :members:

.. currentmodule:: gd

.. autoclass:: xor

.. autoclass:: Coder
    :members:
