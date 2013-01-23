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

.. _jsonrpc: http://jsonrpc.org
