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

.. py:class:: tinyrpc.transports.zmq.ZmqServerTransport

   Server transport based on a :py:const:`zmq.ROUTER` socket.

   :param socket: A :py:const:`zmq.ROUTER` socket instance, bound to an
                  endpoint.

   .. py:method:: create(zmq_context, endpoint)

      Create new server transport.

      Instead of creating the socket yourself, you can call this function and
      merely pass the :py:class:`zmq.core.context.Context` instance.

      By passing a context imported from :py:mod:`zmq.green`, you can use
      green (gevent) 0mq sockets as well.

      :param zmq_context: A 0mq context.
      :param endpoint: The endpoint clients will connect to.

.. py:class:: tinyrpc.transports.zmq.ZmqClientTransport

   Client transport based on a :py:const:`zmq.REQ` socket.

   :param socket: A :py:const:`zmq.REQ` socket instance, connected to the
                  server socket.

   .. py:method:: create(cls, zmq_context, endpoint)

      Create new client transport.

      Instead of creating the socket yourself, you can call this function and
      merely pass the :py:class:`zmq.core.context.Context` instance.

      By passing a context imported from :py:mod:`zmq.green`, you can use
      green (gevent) 0mq sockets as well.

      :param zmq_context: A 0mq context.
      :param endpoint: The endpoint the server is bound to.


HTTP
~~~~

There is only an HTTP client, no server (use WSGI instead).

.. py:class:: tinyrpc.transports.http.HttpPostClientTransport

   HTTP POST based client transport.

   Requires :py:mod:`requests`. Submits messages to a server using the body of
   an ``HTTP`` ``POST`` request. Replies are taken from the responses body.

   :param endpoint: The URL to send ``POST`` data to.
   :param kwargs: Additional parameters for :py:func:`requests.post`.


WSGI
~~~~

.. py:class:: tinyrpc.transports.wsgi.WsgiServerTransport

   WSGI transport.

   Requires :py:mod:`werkzeug`.

   Due to the nature of WSGI, this transport has a few pecularities: It must
   be run in a thread, greenlet or some other form of concurrent execution
   primitive.

   This is due to
   :py:func:`~tinyrpc.transports.wsgi.WsgiServerTransport.handle` blocking
   while waiting for a call to
   :py:func:`~tinyrpc.transports.wsgi.WsgiServerTransport.send_reply`.

   The parameter ``queue_class`` must be used to supply a proper queue class
   for the chosen concurrency mechanism (i.e. when using :py:mod:`gevent`,
   set it to :py:class:`gevent.queue.Queue`).

   :param max_content_length: The maximum request content size allowed. Should
                              be set to a sane value to prevent DoS-Attacks.
   :param queue_class: The Queue class to use.

   .. py:method:: handle()

      WSGI handler function.

      The transport will serve a request by reading the message and putting
      it into an internal buffer. It will then block until another
      concurrently running function sends a reply using
      :py:func:`~tinyrpc.transports.WsgiServerTransport.send_reply`.

      The reply will then be sent to the client being handled and handle will
      return.
