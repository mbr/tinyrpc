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

Table of contents
-----------------

.. toctree::
   :maxdepth: 2

   structure
   protocols
   dispatch

.. _jsonrpc: http://jsonrpc.org
