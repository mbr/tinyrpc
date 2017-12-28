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

Error with data
---------------

The specification_ states that the ``error`` element of a reply may contain
an optional ``data`` property. This property is now available for your use.

There are two ways that you can use to pass additional data with an :py:class:`Exception`.
It depends whether your application generates regular exceptions or exceptions derived
from :py:class:`FixedErrorMessageMixin`.

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

When using :py:class:`FixedErrorMessageMixin` based exceptions the data is passed using
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
