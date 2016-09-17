#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
callback extends the tinyrpc package.

The CallbackServerTransport uses the provided callbacks to implement
communication with the counterpart.

(c) 2016, Leo Noordergraaf, Nextpertise BV
This code is made available under the same license as tinyrpc itself.
"""

import json

from . import ServerTransport

class CallbackServerTransport(ServerTransport):
    """Callback transport.
    Used when tinyrpc is part of a system where it cannot directly attach
    to a socket or stream. The methods ``receive_message`` and ``send_reply``
    are implemented by callback functions that were passed to ``__init__``.

    This transport is also useful for testing the other modules of tinyrpc.
    """
    def __init__(self, reader, writer):
        super(CallbackServerTransport, self).__init__()
        self.reader = reader
        self.writer = writer

    def receive_message(self):
        data = self.reader()
        if type(data) != str:
            data = json.dumps(data)
        return None, data

    def send_reply(self, context, reply):
        self.writer(reply)
