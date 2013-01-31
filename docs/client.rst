RPC Client
==========

:py:class:`~tinyrpc.client.RPCClient` instances are high-level handlers for
making remote procedure calls to servers. Other than
:py:class:`~tinyrpc.client.RPCProxy` objects, they are what most user
applications interact with.

Clients needs to be instantiated with a protocol and a transport to function.
Proxies are syntactic sugar for using clients.

.. autoclass:: tinyrpc.client.RPCClient
   :members:

.. autoclass:: tinyrpc.client.RPCProxy
   :members:
