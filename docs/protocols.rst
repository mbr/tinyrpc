The protocol layer
==================

Any protocol is implemented by deriving from :py:class:`RPCProtocol` and
implementing all of its members:

.. autoclass:: tinyrpc.RPCProtocol
   :members:

These require implementations of the following classes as well:

.. autoclass:: tinyrpc.RPCRequest
   :members:

.. autoclass:: tinyrpc.RPCReply
   :members:

Every protocol deals with three kinds of structures: ``data`` arguments are
always byte strings that are sent via or received from a transport.

The other two are protocol-specific subclasses of
:py:class:`~tinyrpc.RPCRequest` and :py:class:`~tinyrpc.RPCReply`.

Supported protocols
-------------------

Any supported protocol is used by instantiating its classes and calling the
interface of :py:class:`~tinyrpc.RPCProtocol`. Note that constructors are not
part of the interface, any protocol may have specific arguments for its
instances.

Protocols usually live in their own module because they may need to import
optinal modules.

JSON-RPC
~~~~~~~~

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCProtocol
   :members:

.. _jsonrpc: http://jsonrpc.org
