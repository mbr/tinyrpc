ID Generators
=====================

By default, the :py:class:`~tinyrpc.protocols.jsonrpc.JSONRPCProtocol` class 
generates ids as sequential integers starting at 1.
If alternative id generation is needed, you may supply your own
generator or use one from the :py:mod:`~tinyrpc.generators` module.

Example
-------

The following example shows how to use alternative id generators in a protocol
that supports them.

.. code-block:: python

   from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
   from tinyrpc.generators import uuid_generator

   rpc = JSONRPCProtocol(id_generator=uuid_generator())

If a custom generator is required, you may use your own:

.. code-block:: python

    from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
    
    def collatz_generator():
        n = 27
        while True:
            if n % 2 != 0:
                n = 3*n + 1
            else:
                n = n / 2
            yield n

    rpc = JSONRPCProtocol(id_generator=collatz_generator())

API Reference
+++++++++++++
.. automodule:: tinyrpc.generators
    :members:
    :show-inheritance:
    :member-order: bysource