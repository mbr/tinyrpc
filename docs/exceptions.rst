Exception reference
-------------------

.. automodule:: tinyrpc.exc
   :members:


Adding custom exceptions
------------------------

.. note:: As per the specification_ you should use error codes -32000 to
    -32099 when adding server specific error messages.
    Error codes outside the range -32768 to -32000 are available for 
    application specific error codes.

To add custom errors you need to combine an :py:class:`Exception` subclass 
with the :py:class:`FixedErrorMessageMixin` class to create your exception
object which you can raise.

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


.. _specification: http://www.jsonrpc.org/specification#error_object
