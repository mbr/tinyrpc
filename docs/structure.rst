Structure of tinyrpc
====================

``tinyrpc`` architectually considers three layers: Transport, Protocol and
Dispatch.

The Transport-layer is responsible for receiving and sending messages. No
assumptions are made about messages, except that they are of a fixed size.
Messages are received and possibly passed on a Python strings.

On the Protocol-layer messages are decoded into a format that is protocol
independent, these can be passed on to a dispatcher.

The Dispatch-layer performs the actual method calling and serializes the return
value. These can be routed back through the Protocol- and Transport-layer to
return the answer to the calling client.

Each layer is useful "on its own" and can be used seperately. If you simply
need to decode a jsonrpc_ message, without passing it on or sending it through
a transport, any :py:class:`~tinyrpc.RPCProtocol`-class is completely usable
on its own.

CallSpecs
---------

A central data structure in this is the following :py:class:`CallSpec`
structure:

.. py:class:: CallSpec(method, args, kwargs)

   Represents the intent to call a named method with a set of arguments.
   Actually not a class, but a :py:func:`~collections.namedtuple` instance.

   What is acceptable as an argument value type depends on the protocol used.
   A good guess are usually primitive Python types like ``int``, ``float``,
   ``unicode``, ``bool``, ``list`` and ``dict``, as most protocols can
   serialize these.

   :param method: The name of the method to be called.
   :param args:   The arguments to be passed on to the method.
   :param kwargs: The keyword arguments to be passed on to the method.


.. _jsonrpc: http://jsonrpc.org
