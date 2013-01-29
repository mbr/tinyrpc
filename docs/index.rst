tinyrpc: A modular RPC library
==============================

``tinyrpc`` is a library for making and handling RPC calls in python. Its
initial scope is handling jsonrpc_, although it aims to be very well-documented
and modular to make it easy to add support for further protocols.

A feature is support of multiple transports (or none at all) and providing
clever syntactic sugar for writing dispatchers.


Examples
--------

A few examples to get started as fast as possible are included in this
documentation. Ideally, they're all you have to read.

In :doc:`protocols`, you can find client and server examples on how
to use just the protocol parsing parts of ``tinyrpc``.

The :py:class:`~tinyrpc.dispatch.RPCDispatcher` should be useful on its own (or
at least easily replaced with one of your choosing), see :doc:`dispatch` for
details.


Why are there no transports
---------------------------

In version 0.3dev (the current version), there is no implementation for
transports yet, neither is there an interface for them.

When using ``tinyrpc`` to write a server, it is assumed that you're using a
transport that is capable of sending fixed-length messages. Pass these messages
to an instance of :py:class:`~tinyrpc.RPCProtocol` to parse them,
then dispatch the resulting request with
:py:class:`~tinyrpc.dispatch.RPCDispatcher`. Results should be turned into a
response using :py:func:`~tinyrpc.RPCRequest.respond`, which is
then serialized and sent back on the transport.

Clients of the request-reply kind are easier to write: Use
:py:func:`~tinyrpc.RPCProtocol.create_request` to create a request,
pass it to the transport. Wait for a reply and decode it with
:py:func:`~tinyrpc.RPCProtocol.parse_reply`.


Table of contents
-----------------

.. toctree::
   :maxdepth: 2

   structure
   protocols
   dispatch
   transports
   exceptions

.. _jsonrpc: http://jsonrpc.org
