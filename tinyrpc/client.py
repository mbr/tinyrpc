#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .exc import RPCError


class RPCClient(object):
    def __init__(self, protocol, transport):
        self.protocol = protocol
        self.transport = transport

    def _send_and_handle_reply(self, req):
        # sends and waits for reply
        reply = self.transport.send_message(req.serialize())

        response = self.protocol.parse_reply(reply)

        if hasattr(response, 'error'):
            raise RPCError('Error calling remote procedure: %s' %\
                           response.error)

        return response

    def call(self, method, args, kwargs, one_way=False):
        req = self.protocol.create_request(method, args, kwargs, one_way)

        return self._send_and_handle_reply(req).result

    def batch_call(self, calls):
        """Experimental, use at your own peril."""
        req = self.protocol.create_batch_request()

        for call_args in calls:
            req.append(self.protocol.create_request(*call_args))

        return self._send_and_handle_reply(req)


class RPCProxy(object):
    def __init__(self, client, prefix='', one_way=False):
        self.client = client
        self.prefix = prefix
        self.one_way = one_way

    def __getattr__(self, name):
        proxy_func = lambda *args, **kwargs: self.client.call(
                         self.prefix + name,
                         args,
                         kwargs,
                         one_way=self.one_way
                     )
        return proxy_func
