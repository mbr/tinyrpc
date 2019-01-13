#!/usr/bin/env python
# -*- coding: utf-8 -*-

import geventwebsocket as websocket

from . import ClientTransport


class HttpWebSocketClientTransport(ClientTransport):
    """HTTP WebSocket based client transport.

    Requires :py:mod:`websocket-python`. Submits messages to a server using the body of
    an ``HTTP`` ``WebSocket`` message. Replies are taken from the response of the websocket.

    The connection is establish on the ``__init__`` because the protocol is connection oriented,
    you need to close the connection calling the close method.

    :param str endpoint: The URL to connect the websocket.
    :param dict kwargs: Additional parameters for :py:func:`websocket.send`.
    """

    def __init__(self, endpoint, **kwargs):
        self.endpoint = endpoint
        self.request_kwargs = kwargs
        self.ws = websocket.create_connection(self.endpoint, **kwargs)

    def send_message(self, message, expect_reply=True):
        if not isinstance(message, bytes):
            raise TypeError('message must by of type bytes')
        self.ws.send(message)
        r = self.ws.recv()
        if expect_reply:
            return r

    def close(self):
        """Terminate the connection.

        Since WebSocket maintains an open connection over multiple calls
        it must be closed explicitly.
        """
        if self.ws is not None:
            self.ws.close()
