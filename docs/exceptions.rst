The Exceptions hierarchy
========================

All exceptions are rooted in the :py:class:`Exception` class.
The :py:class:`~tinyrpc.exc.RPCError` class derives from it and forms the basis of all tinyrpc exceptions.

Abstract exceptions
-------------------
These exceptions, most of them will be overridden, define errors concerning the transport and structure
of messages.

.. autoclass:: tinyrpc.exc.RPCError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.exc.BadRequestError
    :members:
    :show-inheritance:
    :member-order: bysource
    :noindex:

.. autoclass:: tinyrpc.exc.BadReplyError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.exc.InvalidRequestError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.exc.InvalidReplyError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.exc.MethodNotFoundError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.exc.InvalidParamsError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.exc.ServerError
    :members:
    :show-inheritance:
    :member-order: bysource

Protocol exceptions
-------------------
Each protocol provides its own concrete implementations of these exceptions.

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCParseError
    :members:
    :show-inheritance:
    :member-order: bysource
    :noindex:

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCInvalidRequestError
    :members:
    :show-inheritance:
    :member-order: bysource
    :noindex:

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCMethodNotFoundError
    :members:
    :show-inheritance:
    :member-order: bysource
    :noindex:

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCInvalidParamsError
    :members:
    :show-inheritance:
    :member-order: bysource
    :noindex:

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCInternalError
    :members:
    :show-inheritance:
    :member-order: bysource
    :noindex:

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCServerError
    :members:
    :show-inheritance:
    :member-order: bysource
    :noindex:

This last exception is a client side exception designed to represent the server side error in the client.

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCError
    :members:
    :show-inheritance:
    :member-order: bysource
    :noindex:
