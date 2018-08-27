#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import cgi
import urllib.parse as urlparse

from . import ServerTransport

class CGIServerTransport(ServerTransport):
    """CGI transport.

    The CGIServerTransport adds CGI as a supported server protocol that can be used
    with the regular HTTP client.

    Reading stdin is blocking but, given that we've been called, something is
    waiting.  The transport accepts only POST requests.

    A POST request provides the entire JSON-RPC request in the body of the HTTP
    request.

    With this version support for GET requests is dropped as recommended by
    http://www.simple-is-better.org/json-rpc/transport_http.html.
    """

    def receive_message(self):
        """Receive a message from the transport.

        Blocks until another message has been received. May return a context
        opaque to clients that should be passed on
        :py:func:`~tinyrpc.transport.CGIServerTransport.send_reply` to identify the
        client later on.

        :return: A tuple consisting of ``(context, message)``.
        """

        if not ('REQUEST_METHOD' in os.environ and os.environ['REQUEST_METHOD'] == 'POST'):
            # context isn't used with cgi
            print("Status: 405 Method not Allowed; only POST is accepted")
            exit(0)

        # POST
        content_length = int(os.environ['CONTENT_LENGTH'])
        request_json = sys.stdin.read(content_length)
        request_json = urlparse.unquote(request_json)
        return None, request_json


    def send_reply(self, context, reply):
        """Sends a reply to a client.

        The client is usually identified by passing ``context`` as returned
        from the original
        :py:func:`~tinyrpc.transport.Transport.receive_message` call.

        Messages must be bytes, it is up to the sender to convert the message
        beforehand. A non-bytes value raises a :py:exc:`TypeError`.

        :param context: A context returned by
                        :py:func:`~tinyrpc.transport.CGIServerTransport.receive_message`.
        :param reply: A binary to send back as the reply.
        """

        # context isn't used with cgi
        print("Status: 200 OK")
        print("Content-Type: application/json")
        print("Cache-Control: no-cache")
        print("Pragma: no-cache")
        print("Content-Length: %d" % len(reply))
        print()
        print(reply)

