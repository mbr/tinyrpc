tinyrpc: A modular RPC library
==============================

``tinyrpc`` is a framework for constructing remote procedure call (RPC) services in Python.

In ``tinyrpc`` all components (transport, protocol and dispatcher) that together make an
RPC service are independently replacable.

Although its initial scope is handling jsonrpc_ it is easy to add further protocols or
add additional transports (one such example is msgpackrpc_, which is now fully supported).
If so desired it is even possible to replace the default method dispatcher.


Table of contents
-----------------

.. toctree::
    :maxdepth: 2

    examples
    structure
    dispatch
    protocols
    jsonrpc
    msgpackrpc
    transports
    client
    server
    exceptions

Installation
------------

.. code-block:: sh

   pip install tinyrpc

will install ``tinyrpc`` with its default dependencies.

Optional dependencies
+++++++++++++++++++++

Depending on the protocols and transports you want to use additional dependencies
are required. You can instruct pip to install these dependencies by specifying
extras to the basic install command.

.. code-block:: sh

   pip install tinyrpc[httpclient, wsgi]

will install ``tinyrpc`` with dependencies for the httpclient and wsgi transports.

Available extras are:

+------------+-------------------------------------------------------+
| Option     |  Needed to use objects of class                       |
+============+=======================================================+
| gevent     | optional in RPCClient, required by RPCServerGreenlets |
+------------+-------------------------------------------------------+
| httpclient | HttpPostClientTransport, HttpWebSocketClientTransport |
+------------+-------------------------------------------------------+
| jsonext    | optional in JSONRPCProtocol                           |
+------------+-------------------------------------------------------+
| msgpack    | required by MSGPACKRPCProtocol                        |
+------------+-------------------------------------------------------+
| rabbitmq   | RabbitMQServerTransport, RabbitMQClientTransport      |
+------------+-------------------------------------------------------+
| websocket  | WSServerTransport, HttpWebSocketClientTransport       |
+------------+-------------------------------------------------------+
| wsgi       | WsgiServerTransport                                   |
+------------+-------------------------------------------------------+
| zmq        | ZmqServerTransport, ZmqClientTransport                |
+------------+-------------------------------------------------------+

People
------

Creator
+++++++

- Marc Brinkmann: https://github.com/mbr

    As of this writing (in Jan 2013) there are a few jsonrpc_ libraries already out
    there on PyPI_, most of them handling one specific use case (e.g. json via
    WSGI, using Twisted, or TCP-sockets).

    None of the libraries, however, made it easy to reuse the jsonrpc_-parsing bits
    and substitute a different transport (i.e. going from json_ via TCP_ to an
    implementation using WebSockets_ or 0mq_).

    In the end, all these libraries have their own dispatching interfaces and a
    custom implementation of handling jsonrpc_.

    ``tinyrpc`` aims to do better by dividing the problem into cleanly
    interchangeable parts that allow easy addition of new transport methods, RPC
    protocols or dispatchers.

Maintainer
++++++++++

- Leo Noordergraaf: https://github.com/lnoor

    Looking for a Python jsonrpc_ library I found ``tinyrpc``.
    I was immediately taken by its modular concept and construction.

    After creating a couple transports and trying to get them integrated in tinyrpc,
    I learned that Marc got involved with other projects and that maintaining
    ``tinyrpc`` became too much a burden.
    I then volunteered to become its maintainer.

.. _jsonrpc: http://jsonrpc.org
.. _msgpackrpc: https://github.com/msgpack-rpc/msgpack-rpc/blob/master/spec.md
.. _PyPI: http://pypi.python.org
.. _json: http://www.json.org/
.. _TCP: http://en.wikipedia.org/wiki/Transmission_Control_Protocol
.. _WebSockets: http://en.wikipedia.org/wiki/WebSocket
.. _0mq: http://www.zeromq.org/
