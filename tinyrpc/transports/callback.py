#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json

from . import ServerTransport

class CallbackServerTransport(ServerTransport):
    """Callback server transport.

    The CallbackServerTransport uses the provided callbacks to implement
    communication with the counterpart.

    Used when tinyrpc is part of a system where it cannot directly attach
    to a socket or stream. The methods :py:meth:`receive_message` and
    :py:meth:`send_reply` are implemented by callback functions that are
    set when constructed.

    This transport is also useful for testing the other modules of tinyrpc.

    :param callable reader: Expected to return a binary datum.
    :param callable writer: Expected to accept a single parameter of type binary.
    """
    def __init__(self, reader, writer):
        super(CallbackServerTransport, self).__init__()
        self.reader = reader
        self.writer = writer

    def receive_message(self):
        """Receive a message from the transport.

        Uses the callback function :py:attr:`reader` to obtain a binary.
        May return a context opaque to clients that should be passed on
        :py:meth:`send_reply` to identify the client later on.

        :return: A tuple consisting of ``(context, message)``.
        """
        return None, self.reader()

    def send_reply(self, context, reply):
        """Sends a reply to a client.

        The client is usually identified by passing ``context`` as returned
        from the original :py:meth:`receive_message` call.

        Uses the callback function :py:attr:`writer` to forward the binary
        reply parameter.

        :param context: A context returned by :py:meth:`receive_message`.
        :param reply: A binary to send back as the reply.
        """

        self.writer(reply)
