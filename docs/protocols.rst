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


Supported protocols
-------------------

Any supported protocol is used by instantiating its class and calling the
interface of :py:class:`~tinyrpc.protocols.RPCProtocol`. Note that constructors
are not part of the interface, any protocol may have specific arguments for its
instances.

Protocols usually live in their own module because they may need to import
optional modules that needn't be a dependency for all of ``tinyrpc``.

Example
-------

The following example shows how to use the
:py:class:`~tinyrpc.protcols.jsonrpc.JSONRPCProtocol` class in a custom
application, without using any other components:

Server
++++++

.. code-block:: python

   from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
   from tinyrpc import BadRequestError, RPCBatchRequest

   rpc = JSONRPCProtocol()

   # the code below is valid for all protocols, not just JSONRPC:

   def handle_incoming_message(self, data):
       try:
           request = rpc.parse_request(data)
       except BadRequestError as e:
           # request was invalid, directly create response
           response = e.error_respond(e)
       else:
           # we got a valid request
           # the handle_request function is user-defined
           # and returns some form of response
           if hasattr(request, create_batch_response):
               response = request.create_batch_response(
                   handle_request(req) for req in request
               )
           else:
               response = handle_request(request)

       # now send the response to the client
       if response != None:
            send_to_client(response.serialize())


   def handle_request(request):
       try:
           # do magic with method, args, kwargs...
           return request.respond(result)
       except Exception as e:
           # for example, a method wasn't found
           return request.error_respond(e)

Client
++++++

.. code-block:: python

   from tinyrpc.protocols.jsonrpc import JSONRPCProtocol

   rpc = JSONRPCProtocol()

   # again, code below is protocol-independent

   # assuming you want to call method(*args, **kwargs)

   request = rpc.create_request(method, args, kwargs)
   reply = send_to_server_and_get_reply(request)

   response = rpc.parse_reply(reply)

   if hasattr(response, 'error'):
       # error handling...
   else:
       # the return value is found in response.result
       do_something_with(response.result)


Another example, this time using batch requests:

.. code-block:: python

   # or using batch requests:

   requests = rpc.create_batch_request([
       rpc.create_request(method_1, args_1, kwargs_1)
       rpc.create_request(method_2, args_2, kwargs_2)
       # ...
   ])

   reply = send_to_server_and_get_reply(request)

   responses = rpc.parse_reply(reply)

   for responses in response:
       if hasattr(reponse, 'error'):
           # ...


Finally, one-way requests are requests where the client does not expect an
answer:

.. code-block:: python

   request = rpc.create_request(method, args, kwargs, one_way=True)
   send_to_server(request)

   # done


.. _jsonrpc: http://jsonrpc.org
