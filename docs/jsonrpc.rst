The JSON-RPC protocol
=====================

Example
-------

The following example shows how to use the
:py:class:`~tinyrpc.protocols.jsonrpc.JSONRPCProtocol` class in a custom
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


Protocol implementation
-----------------------

API Reference
+++++++++++++

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCProtocol
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCRequest
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCSuccessResponse
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCErrorResponse
    :members:
    :show-inheritance:
    :member-order: bysource

Batch protocol
--------------

API Reference
+++++++++++++

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCBatchRequest
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCBatchResponse
    :members:
    :show-inheritance:
    :member-order: bysource


Errors and error handling
-------------------------

API Reference
+++++++++++++

.. autoclass:: tinyrpc.protocols.jsonrpc.FixedErrorMessageMixin
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCParseError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCInvalidRequestError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCMethodNotFoundError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCInvalidParamsError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCInternalError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCServerError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.jsonrpc.JSONRPCError
    :members:
    :show-inheritance:
    :member-order: bysource

Adding custom exceptions
------------------------

.. note:: As per the specification_ you should use error codes -32000 to
    -32099 when adding server specific error messages.
    Error codes outside the range -32768 to -32000 are available for
    application specific error codes.

To add custom errors you need to combine an :py:class:`Exception` subclass
with the :py:class:`~tinyrpc.protocols.jsonrpc.FixedErrorMessageMixin` class to
create your exception object which you can raise.

So a version of the reverse string example that dislikes palindromes could
look like:


.. code-block:: python

    from tinyrpc.protocols.jsonrpc import FixedErrorMessageMixin, JSONRPCProtocol
    from tinyrpc.dispatch import RPCDispatcher

    dispatcher = RPCDispatcher()

    class PalindromeError(FixedErrorMessageMixin, Exception):
        jsonrpc_error_code = 99
        message = "Ah, that's cheating!"


    @dispatcher.public
    def reverse_string(s):
        r = s[::-1]
        if r == s:
            raise PalindromeError()
        return r

Error with data
---------------

The specification_ states that the ``error`` element of a reply may contain
an optional ``data`` property. This property is now available for your use.

There are two ways that you can use to pass additional data with an :py:class:`Exception`.
It depends whether your application generates regular exceptions or exceptions derived
from :py:class:`~tinyrpc.protocols.jsonrpc.FixedErrorMessageMixin`.

When using ordinary exceptions you normally pass a single parameter (an error message)
to the :py:class:`Exception` constructor.
By passing two parameters, the second parameter is assumed to be the data element.

.. code-block:: python

    @public
    def fn():
        raise Exception('error message', {'msg': 'structured data', 'lst': [1, 2, 3]})

This will produce the reply message::

    {   "jsonrpc": "2.0",
        "id": <some id>,
        "error": {
            "code": -32000,
            "message": "error message",
            "data": {"msg": "structured data", "lst": [1, 2, 3]}
        }
    }

When using :py:class:`~tinyrpc.protocols.jsonrpc.FixedErrorMessageMixin` based exceptions the data is passed using
a keyword parameter.

.. code-block:: python

    class MyException(FixedErrorMessageMixin, Exception):
        jsonrcp_error_code = 99
        message = 'standard message'

    @public
    def fn():
        raise MyException(data={'msg': 'structured data', 'lst': [1, 2, 3]})

This will produce the reply message::

    {   "jsonrpc": "2.0",
        "id": <some id>,
        "error": {
            "code": 99,
            "message": "standard message",
            "data": {"msg": "structured data", "lst": [1, 2, 3]}
        }
    }


.. _specification: http://www.jsonrpc.org/specification#error_object
