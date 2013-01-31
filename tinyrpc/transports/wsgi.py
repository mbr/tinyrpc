#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Queue

from werkzeug.wrappers import Response, Request

from . import ServerTransport


class WsgiServerTransport(ServerTransport):
    def __init__(self, max_content_length=4096, queue_class=Queue.Queue):
        self.messages = queue_class()
        self.replies = queue_class()
        self.current_context = 0
        self.max_content_length = max_content_length

    def receive_message(self):
        msg = self.messages.get()
        self.current_context += 1
        return self.current_context, msg

    def send_reply(self, context, reply):
        if not isinstance(reply, str):
            raise TypeError('str expected')
        if not context == self.current_context:
            raise RuntimeError('Must send reply after receiving message')

        self.replies.put(reply)

    def handle(self, environ, start_response):
        request = Request(environ)
        request.max_content_length = self.max_content_length

        if request.method == 'POST':
            response = Response('Bla bla bla', 500)
            # message is encoded in POST, read it and send reply
            self.messages.put(request.stream.read())
            response = Response(self.replies.get())
        else:
            # nothing else supported at the moment
            response = Response('Only POST supported', 405)

        return response(environ, start_response)
