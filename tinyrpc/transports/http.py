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

    def send_message(self, message, expect_reply=True):
        if not isinstance(message, str):
            raise TypeError('str expected')

        r = requests.post(self.endpoint, data=message, **self.request_kwargs)

        if expect_reply:
            return r.data
