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

    def _run_background(self):
        while True:
            message = self.request_queue.get()
            if message == None:
                break

    def send_message(self, message):
        if not isinstance(message, str):
            raise TypeError('str expected')

        self._response = requests.post(self.endpoint, data=message, **self.request_kwargs)


    def receive_reply(self):
        assert self._response

        return self._reponse.data
