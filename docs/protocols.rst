The protocol layer
==================

Any protocol is implemented by deriving from :py:class:`RPCProtocol` and
implementing all of its members:

.. autoclass:: tinyrpc.RPCProtocol
   :members:

These require implementations of the following classes as well:

.. autoclass:: tinyrpc.RPCRequest
   :members:

.. autoclass:: tinyrpc.RPCResponse
   :members:

.. autoclass:: tinyrpc.RPCSuccessResponse
   :members:

.. autoclass:: tinyrpc.RPCErrorResponse
   :members:

Every protocol deals with three kinds of structures: ``data`` arguments are
always byte strings, either messages or replies, that are sent via or received
from a transport.

The other two are protocol-specific subclasses of
:py:class:`~tinyrpc.RPCRequest` and :py:class:`~tinyrpc.RPCReply`, the latter
knows two subclasses for successful and unsuccessful requests.

Supported protocols
-------------------

Any supported protocol is used by instantiating its classes and calling the
interface of :py:class:`~tinyrpc.RPCProtocol`. Note that constructors are not
part of the interface, any protocol may have specific arguments for its
instances.

Protocols usually live in their own module because they may need to import
optinal modules.

Example
-------

The following example shows how to use the
:py:class:`~tinyrpc.protcols.jsonrpc.JSONRPCProtocol` class in a custom
application, without using any other components:

Server
~~~~~~

.. code-block:: python

   from tinyrpc.protocols.jsonrpc import JSONRPCProtocol

   rpc = JSONRPCProtocol()

   # the code below is valid for all protocols, not just JSONRPC:

   def handle_incoming_message(self, data):
       try:
           request = rpc.parse_request(data)
       except Exception as e:
           response = rpc.create_error_response(e)
       else:
           # we got a valid request
           try:
               # at this point, response.method, response.args and response.kwargs
               # can be used to determine a result
               response = request.respond(result)
           except Exception as e:
               # for example, a method wasn't found
               response = request.error_respond(e)

       # now send the response to the client
       send_to_client(response.serialize())

Client
~~~~~~

.. code-block:: python

   from tinyrpc.protocols.jsonrpc import JSONRPCProtocol

   rpc = JSONRPCProtocol()

   # again, code below is protocol-independent

   # assuming you want to call method(*args, **kwargs)

   request = rpc.create_request(method, args, kwargs)
   reply = send_to_server_and_get_reply(request)

   response = rpc.parse_reply(reply)

   if response.is_error:
       # error handling...
   else:
       # the return value is found in response.rv


JSON-RPC
~~~~~~~~

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCProtocol
   :members:

.. _jsonrpc: http://jsonrpc.org
