Transports
==========

Transports are somewhat low level interface concerned with transporting
messages across through different means. "Messages" in this case are simple
strings. All transports need to support two different interfaces:

.. autoclass:: tinyrpc.transports.ServerTransport
   :members:

.. autoclass:: tinyrpc.transports.ClientTransport
   :members:

Note that these transports are of relevance when using ``tinyrpc``-built in
facilities. They can be coopted for any other purpose, if you simply need
reliable server-client message passing as well.

Transport implementations
-------------------------

A few transport implementations are included with ``tinyrpc``:

0mq
~~~

Based on :py:mod:`zmq`, supports 0mq based sockets. Highly recommended:

.. autoclass:: tinyrpc.transports.zmq.ZmqServerTransport
   :members:

.. autoclass:: tinyrpc.transports.zmq.ZmqClientTransport
   :members:

HTTP
~~~~

There is only an HTTP client, no server (use WSGI instead).

.. autoclass:: tinyrpc.transports.http.HttpPostClientTransport
   :members:

WSGI
~~~~

.. autoclass:: tinyrpc.transports.wsgi.WsgiServerTransport
   :members:
