Server implementations
======================

Like :doc:`client`, servers are top-level instances that most user code should
interact with. They provide runnable functions that are combined with
transports, protocols and dispatchers to form a complete RPC system.

.. automodule:: tinyrpc.server
   :members:

.. py:class:: tinyrpc.server.gevent.RPCServerGreenlets

   Asynchronous RPCServer.

   This implementation of :py:class:`~tinyrpc.server.RPCServer` uses
   :py:func:`gevent.spawn` to spawn new client handlers, result in asynchronous
   handling of clients using greenlets.
