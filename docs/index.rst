tinyrpc: A modular RPC library
==============================

``tinyrpc`` is a library for making and handling RPC calls in python. Its
initial scope is handling jsonrpc_, although it aims to be very well-documented
and modular to make it easy to add support for further protocols.

A feature is support of multiple transports (or none at all) and providing
clever syntactic sugar for writing dispatchers.

.. toctree::
   :maxdepth: 2

   structure
   protocols

.. _jsonrpc: http://jsonrpc.org
