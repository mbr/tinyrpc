#!/usr/bin/env python
# -*- coding: utf-8 -*-

# FIXME: needs unittests
# FIXME: needs checks for out-of-order, concurrency, etc as attributes
from tinyrpc.exc import RPCError

class RPCServer(object):
    """High level RPC server.

    :param transport: The :py:class:`~tinyrpc.transports.RPCTransport` to use.
    :param protocol: The :py:class:`~tinyrpc.RPCProtocol` to use.
    :param dispatcher: The :py:class:`~tinyrpc.dispatch.RPCDispatcher` to use.
    """
    def __init__(self, transport, protocol, dispatcher):
        self.transport = transport
        self.protocol = protocol
        self.dispatcher = dispatcher

    def serve_forever(self):
        """Handle requests forever.

        Starts the server loop continuously calling :py:meth:`receive_one_message`
        to process the next incoming request.
        """
        while True:
            self.receive_one_message()

    def receive_one_message(self):
        """Handle a single request.

        Polls the transport for a new message.
        
        After a new message has arrived :py:meth:`_spawn` is called with a handler
        function and arguments to handle the request.

        The handler function will try to decode the message using the supplied
        protocol, if that fails, an error response will be sent. After decoding
        the message, the dispatcher will be asked to handle the resultung
        request and the return value (either an error or a result) will be sent
        back to the client using the transport.
        """
        context, message = self.transport.receive_message()

        # assuming protocol is threadsafe and dispatcher is theadsafe, as
        # long as its immutable

        def handle_message(context, message):
            try:
                request = self.protocol.parse_request(message)
            except RPCError as e:
                response = e.error_respond()
            else:
                response = self.dispatcher.dispatch(
                    request, 
                    getattr(self.protocol, '_caller', None)
                )

            # send reply
            self.transport.send_reply(context, response.serialize())

        self._spawn(handle_message, context, message)

    def _spawn(self, func, *args, **kwargs):
        """Spawn a handler function.

        This function is overridden in subclasses to provide concurrency.

        In the base implementation, it simply calls the supplied function
        ``func`` with ``*args`` and ``**kwargs``. This results in a
        single-threaded, single-process, synchronous server.

        :param func: A callable to call.
        :param args: Arguments to ``func``.
        :param kwargs: Keyword arguments to ``func``.
        """
        func(*args, **kwargs)
