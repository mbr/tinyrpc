tinyrpc: A modular RPC library
==============================

``tinyrpc`` is a library for making and handling RPC calls in python. Its
initial scope is handling jsonrpc_, although it aims to be very well-documented
and modular to make it easy to add support for further protocols.

A feature is support of multiple transports (or none at all) and providing
clever syntactic sugar for writing dispatchers.

Quickstart examples
-------------------

The source contains all of these examples in a working fashion in the examples
subfolder.

HTTP based
~~~~~~~~~~

A client making JSONRPC calls via HTTP (this requires :py:mod:`requests` to be
installed):

.. code-block:: python

   from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
   from tinyrpc.transports.http import HttpPostClientTransport
   from tinyrpc import RPCClient

   rpc_client = RPCClient(
       JSONRPCProtocol(),
       HttpPostClientTransport('http://example.org/jsonrpc/2.0/')
   )

   time_server = rpc_client.get_proxy()

   # ...

   # call a method called 'get_time_in' with a single string argument
   time_in_berlin = time_server.get_time_in('Europe/Berlin')

These can be answered by a server implemented as follows:

.. code-block:: python

   import gevent
   import gevent.wsgi
   import gevent.queue
   from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
   from tinyrpc.transports.wsgi import WsgiServerTransport
   from tinyrpc.server.gevent import RPCServerGreenlets
   from tinyrpc.dispatch import RPCDispatcher

   dispatcher = RPCDispatcher()
   transport = WsgiServerTransport(queue_class=gevent.queue.Queue)

   # start wsgi server as a background-greenlet
   wsgi_server = gevent.wsgi.WSGIServer(('127.0.0.1', 80), transport.handle)
   gevent.spawn(wsgi_server.serve_forever)

   rpc_server = RPCServerGreenlets(
       transport,
       JSONRPCProtocol(),
       dispatcher
   )

   @dispatcher.public
   def reverse_string(s):
       return s[::-1]

   # in the main greenlet, run our rpc_server
   rpc_server.serve_forever()


Further examples
----------------

In :doc:`protocols`, you can find client and server examples on how
to use just the protocol parsing parts of ``tinyrpc``.

The :py:class:`~tinyrpc.dispatch.RPCDispatcher` should be useful on its own (or
at least easily replaced with one of your choosing), see :doc:`dispatch` for
details.



Table of contents
-----------------

.. toctree::
   :maxdepth: 2

   structure
   protocols
   dispatch
   transports
   client
   server
   exceptions

.. _jsonrpc: http://jsonrpc.org
