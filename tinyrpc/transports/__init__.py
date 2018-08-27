#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ServerTransport(object):
    """Base class for all server transports."""

    def receive_message(self):
        """Receive a message from the transport.

        Blocks until another message has been received. May return a context
        opaque to clients that should be passed on to
        :py:func:`~tinyrpc.transport.ServerTransport.send_reply` to identify
        the client later on.

        The message must be treated as a binary datum since only the protocol
        level will know how to interpret the message.
        However, some transports may need to encode the message in some way
        in order to be able to successfully transport the message. It is the
        responsibility of the transport layer at the opposite side to properly
        decode the message.

        :return: A tuple consisting of ``(context, message)``.
        """
        raise NotImplementedError()

    def send_reply(self, context, reply):
        """Sends a reply to a client.

        The client is usually identified by passing ``context`` as returned
        from the original
        :py:func:`~tinyrpc.transport.Transport.receive_message` call.

        The reply must be treated as a binary datum since only the protocol
        level will know how to construct the reply.
        However, some transports may need to encode the reply in some way
        in order to be able to successfully transport the reply. It is the
        responsibility of the transport layer at the opposite side to properly
        decode the reply.

        :param context: A context returned by
                        :py:func:`~tinyrpc.transport.ServerTransport.receive_message`.
        :param reply: A binary datum to send back as the reply.
        """
        raise NotImplementedError


class ClientTransport(object):
    """Base class for all client transports."""

    def send_message(self, message, expect_reply=True):
        """Send a message to the server and possibly receive a reply.

        Sends a message to the connected server.

        The message must be treated as a binary datum since only the protocol
        level will know how to interpret the message.
        However, some transports may need to encode the message in some way
        in order to be able to successfully transport the message. It is the
        responsibility of the transport layer at the opposite side to properly
        decode the message.

        This function will block until one reply has been received.

        :param message: A binary datum to send.
        :return: A binary datum containing the server reply.
        """
        raise NotImplementedError
