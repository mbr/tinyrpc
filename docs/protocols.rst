The protocol layer
==================

Interface definition
--------------------

All protocols are implemented by deriving from :py:class:`~tinyrpc.protocols.RPCProtocol`
and implementing all of its members.

Every protocol deals with multiple kinds of structures: ``data`` arguments are
always byte strings, either messages or replies, that are sent via or received
from a transport.

Protocol-specific subclasses of :py:class:`~tinyrpc.protocols.RPCRequest` and
:py:class:`~tinyrpc.protocols.RPCResponse` represent well-formed requests and responses.

Protocol specific subclasses of :py:class:`~tinyrpc.protocols.RPCErrorResponse` represent
errors and error responses.

Finally, if an error occurs during parsing of a request, a
:py:class:`~tinyrpc.exc.BadRequestError` instance must be thrown. These need to be
subclassed for each protocol as well, since they generate error replies.

API Reference
+++++++++++++

.. autoclass:: tinyrpc.protocols.RPCProtocol
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.RPCRequest
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.RPCResponse
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.RPCErrorResponse
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.exc.BadRequestError
    :members:
    :show-inheritance:
    :member-order: bysource


Batch protocols
---------------

Some protocols may support batch requests. In this case, they need to derive
from :py:class:`~tinyrpc.protocols.RPCBatchProtocol`.

Batch protocols differ in that their
:py:func:`~tinyrpc.protocols.RPCProtocol.parse_request` method may return an instance of
:py:class:`~tinyrpc.protocols.RPCBatchRequest`. They also possess an addional method in
:py:func:`~tinyrpc.protocols.RPCBatchProtocol.create_batch_request`.

Handling a batch request is slightly different, while it supports
:py:func:`~tinyrpc.protocols.RPCBatchRequest.error_respond`, to make actual responses,
:py:func:`~tinyrpc.protocols.RPCBatchRequest.create_batch_response` needs to be used.

No assumptions are made whether or not it is okay for batch requests to be
handled in parallel. This is up to the server/dispatch implementation, which
must be chosen appropriately.

API Reference
+++++++++++++

.. autoclass:: tinyrpc.protocols.RPCBatchProtocol
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.RPCBatchRequest
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.RPCBatchResponse
    :members:
    :show-inheritance:
    :member-order: bysource


ID Generators
-------------

By default, the :py:class:`~tinyrpc.protocols.jsonrpc.JSONRPCProtocol` 
and :py:class:`~tinyrpc.protocols.msgpackrpc.MSGPACKRPCProtocol` classes
generates ids as sequential integers starting at 1.
If alternative id generation is needed, you may supply your own
generator.

Example
-------

The following example shows how to use alternative id generators in a protocol
that supports them.

.. code-block:: python

    from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
    
    def collatz_generator():
        """A sample generator for demonstration purposes ONLY."""
        n = 27
        while True:
            if n % 2 != 0:
                n = 3*n + 1
            else:
                n = n / 2
            yield n

    rpc = JSONRPCProtocol(id_generator=collatz_generator())


Supported protocols
-------------------

Any supported protocol is used by instantiating its class and calling the
interface of :py:class:`~tinyrpc.protocols.RPCProtocol`. Note that constructors
are not part of the interface, any protocol may have specific arguments for its
instances.

Protocols usually live in their own module because they may need to import
optional modules that needn't be a dependency for all of ``tinyrpc``.

.. _jsonrpc: http://jsonrpc.org
