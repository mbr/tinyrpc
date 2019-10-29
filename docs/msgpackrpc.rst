The MSGPACK-RPC protocol
========================

Example
-------

The following example shows how to use the
:py:class:`~tinyrpc.protocols.msgpackrpc.MSGPACKRPCProtocol` class in a custom
application, without using any other components:

Server
++++++

.. code-block:: python

   from tinyrpc.protocols.msgpackrpc import MSGPACKRPCProtocol
   from tinyrpc import BadRequestError, RPCRequest

   rpc = MSGPACKRPCProtocol()

   # the code below is valid for all protocols, not just MSGPACKRPCProtocol,
   # as long as you don't need to handle batch RPC requests:

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

   from tinyrpc.protocols.msgpackrpc import MSGPACKRPCProtocol

   rpc = MSGPACKRPCProtocol()

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

.. autoclass:: tinyrpc.protocols.msgpackrpc.MSGPACKRPCProtocol
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.msgpackrpc.MSGPACKRPCRequest
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.msgpackrpc.MSGPACKRPCSuccessResponse
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.msgpackrpc.MSGPACKRPCErrorResponse
    :members:
    :show-inheritance:
    :member-order: bysource

Errors and error handling
-------------------------

API Reference
+++++++++++++

.. autoclass:: tinyrpc.protocols.msgpackrpc.FixedErrorMessageMixin
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.msgpackrpc.MSGPACKRPCParseError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.msgpackrpc.MSGPACKRPCInvalidRequestError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.msgpackrpc.MSGPACKRPCMethodNotFoundError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.msgpackrpc.MSGPACKRPCInvalidParamsError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.msgpackrpc.MSGPACKRPCInternalError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.msgpackrpc.MSGPACKRPCServerError
    :members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.protocols.msgpackrpc.MSGPACKRPCError
    :members:
    :show-inheritance:
    :member-order: bysource

Adding custom exceptions
------------------------

.. note:: Unlike JSON-RPC, the MSGPACK-RPC specification does not specify how
    the error messages should look like; the protocol allows any arbitrary
    MSGPACK object as an error object. For sake of compatibility with JSON-RPC,
    this implementation uses MSGPACK lists of length 2 (consisting of a numeric
    error code and an error description) to represent errors in the serialized
    representation. These are transparently decoded into
    :py:class:`~tinyrpc.protocols.msgpackrpc.MSGPACKRPCError` instances as
    needed. The error codes for parsing errors, invalid requests, unknown RPC
    methods and so on match those from the `JSON-RPC specification`_.

To add custom errors you need to combine an :py:class:`Exception` subclass
with the :py:class:`~tinyrpc.protocols.msgpackrpc.FixedErrorMessageMixin` class
to create your exception object which you can raise.

So a version of the reverse string example that dislikes palindromes could
look like:


.. code-block:: python

    from tinyrpc.protocols.msgpackrpc import FixedErrorMessageMixin, MSGPACKRPCProtocol
    from tinyrpc.dispatch import RPCDispatcher

    dispatcher = RPCDispatcher()

    class PalindromeError(FixedErrorMessageMixin, Exception):
        msgpackrpc_error_code = 99
        message = "Ah, that's cheating!"


    @dispatcher.public
    def reverse_string(s):
        r = s[::-1]
        if r == s:
            raise PalindromeError()
        return r

.. _specification: https://github.com/msgpack-rpc/msgpack-rpc/blob/master/spec.md
.. _JSON-RPC specification: http://www.jsonrpc.org/specification#error_object
