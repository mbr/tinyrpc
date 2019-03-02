Transports
==========

Transports are somewhat low level interface concerned with transporting
messages across through different means. "Messages" in this case are simple
strings. All transports need to support two different interfaces:

.. autoclass:: tinyrpc.transports.ServerTransport
    :members:
    :noindex:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.transports.ClientTransport
    :members:
    :noindex:
    :show-inheritance:
    :member-order: bysource

Note that these transports are of relevance when using ``tinyrpc``-built in
facilities. They can be coopted for any other purpose, if you simply need
reliable server-client message passing as well.

Also note that the client transport interface is not designed for asynchronous
use. For simple use cases (sending multiple concurrent requests) monkey patching
with gevent may get the job done.


Transport implementations
-------------------------

A few transport implementations are included with ``tinyrpc``:

0mq
~~~

Based on :py:mod:`zmq`, supports 0mq based sockets. Highly recommended:

.. autoclass:: tinyrpc.transports.zmq.ZmqServerTransport
    :members:
    :noindex:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.transports.zmq.ZmqClientTransport
    :members:
    :noindex:
    :show-inheritance:
    :member-order: bysource

HTTP
~~~~

There is only an HTTP client, no server (use WSGI instead).

.. autoclass:: tinyrpc.transports.http.HttpPostClientTransport
    :members:
    :noindex:
    :show-inheritance:
    :member-order: bysource

.. note:: To set a timeout on your client transport provide a ``timeout``
    keyword parameter like::

        transport = HttpPostClientTransport(endpoint, timeout=0.1)

    It will result in a ``requests.exceptions.Timeout`` exception when a
    timeout occurs.

WSGI
~~~~

.. autoclass:: tinyrpc.transports.wsgi.WsgiServerTransport
    :members:
    :noindex:
    :show-inheritance:
    :member-order: bysource

CGI
~~~

.. autoclass:: tinyrpc.transports.cgi.CGIServerTransport
    :members:
    :noindex:
    :show-inheritance:
    :member-order: bysource

Callback
~~~~~~~~

.. autoclass:: tinyrpc.transports.callback.CallbackServerTransport
    :members:
    :noindex:
    :show-inheritance:
    :member-order: bysource

WebSocket
~~~~~~~~~

.. autoclass:: tinyrpc.transports.websocket.WSServerTransport
    :members:
    :noindex:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.transports.websocket.WSApplication
    :members:
    :noindex:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: tinyrpc.transports.websocketclient.HttpWebSocketClientTransport
    :members:
    :noindex:
    :show-inheritance:
    :member-order: bysource

