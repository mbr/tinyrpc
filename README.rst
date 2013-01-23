tinyrpc: A small and modular way of handling web-related RPC
============================================================

Motivation
----------

As of this writing (in Jan 2013) there are a few jsonrpc_ libraries already out
there on PyPI_, most of them handling one specific use case (i.e. json via
WSGI, using Twisted, or TCP-sockets).

None of the libraries, however, made it easy to reuse the jsonrpc_-parsing bits
and substitute a different transport (i.e. going from json_ via TCP_ to an
implementation using WebSockets_ or 0mq_).

In the end, all these libraries have their own dispatching interfaces and a
custom implementation of handling jsonrpc_.

``tinyrpc`` aims to do better by dividing the problem into cleanly
interchangeable parts that allow easy addition of new transport methods, RPC
protocols or dispatchers.

Structure of tinyrpc
--------------------

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
a transport, the ``JSONRPCProtocol``-class is completely usable on its own.

Protocols
---------

Currently, only jsonrpc_ is supported[#]_.

.. [#]: tinyrpc started out as a jsonrpc_ library because that was the
   immediate need when it was written. Its structure should make it very
   straight-forward to implement other RPC schemes though.
.. _jsonrpc: http://www.jsonrpc.org/
.. _PyPI: http://pypi.python.org
.. _json: http://www.json.org/
.. _TCP: http://en.wikipedia.org/wiki/Transmission_Control_Protocol
.. _WebSockets: http://en.wikipedia.org/wiki/WebSocket
.. _0mq: http://www.zeromq.org/
