#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import  # needed for zmq import

from typing import Tuple, Any

import zmq

from . import ServerTransport, ClientTransport


class ZmqServerTransport(ServerTransport):
    """Server transport based on a :py:const:`zmq.ROUTER` socket.

    :param socket: A :py:const:`zmq.ROUTER` socket instance, bound to an
                   endpoint.
    """

    def __init__(self, socket: zmq.Socket) -> None:
        self.socket = socket

    def receive_message(self) -> Tuple[Any, bytes]:
        msg = self.socket.recv_multipart()
        return msg[:-1], msg[-1]

    def send_reply(self, context: Any, reply: bytes) -> None:
        self.socket.send_multipart(context + [reply])

    @classmethod
    def create(cls, zmq_context: zmq.Context, endpoint: str) -> 'ZmqServerTransport':
        """Create new server transport.

        Instead of creating the socket yourself, you can call this function and
        merely pass the :py:class:`zmq.core.context.Context` instance.

        By passing a context imported from :py:mod:`zmq.green`, you can use
        green (gevent) 0mq sockets as well.

        :param zmq_context: A 0mq context.
        :param endpoint: The endpoint clients will connect to.
        """
        socket = zmq_context.socket(zmq.ROUTER)
        socket.bind(endpoint)
        return cls(socket)


class ZmqClientTransport(ClientTransport):
    """Client transport based on a :py:const:`zmq.REQ` socket.

    :param socket: A :py:const:`zmq.REQ` socket instance, connected to the
                   server socket.
    """

    def __init__(self, socket: zmq.Socket) -> None:
        self.socket = socket

    def send_message(self, message: bytes, expect_reply: bool = True) -> bytes:
        self.socket.send(message)

        if expect_reply:
            return self.socket.recv()

    @classmethod
    def create(cls, zmq_context: zmq.Context, endpoint: str) -> 'ZmqClientTransport':
        """Create new client transport.

        Instead of creating the socket yourself, you can call this function and
        merely pass the :py:class:`zmq.core.context.Context` instance.

        By passing a context imported from :py:mod:`zmq.green`, you can use
        green (gevent) 0mq sockets as well.

        :param zmq_context: A 0mq context.
        :param endpoint: The endpoint the server is bound to.
        """
        socket = zmq_context.socket(zmq.REQ)
        socket.connect(endpoint)
        return cls(socket)
