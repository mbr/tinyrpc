#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Queue import Queue
import threading
import requests

from . import ServerTransport, ClientTransport


class HttpPostClientTransport(ClientTransport):
    def __init__(self, endpoint, **kwargs):
        self.endpoint = endpoint
        self.request_kwargs = kwargs

        self.request_queue = Queue()
        self.reply_queue = Queue()

        self._background_thread = threading.Thread(target=self._run_background)
        self._background_thread.daemon = True
        self._background_thread.start()

    def __del__(self):
        self.request_queue.put(None)
        self._background_thread.join()
        super(HttpPostClientTransport, self).__del__()

    def _run_background(self):
        while True:
            message = self.request_queue.get()
            if message == None:
                break

            try:
                r = requests.post(self.endpoint, data=message, **self.request_kwargs)
            except Exception as e:
                self.reply_queue.put(e)
            else:
                self.reply_queue.put(r)

    def send_message(self, message):
        if not isinstance(message, str):
            raise TypeError('str expected')

        self.request_queue.put(message)

    def receive_reply(self):
        reply = self.request_queue.get()

        if isinstance(reply, Exception):
            raise reply

        return reply
