#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from tinyrpc.client import RPCClient
from tinyrpc.transports import ClientTransport
from tinyrpc.protocols import RPCProtocol, RPCRequest, RPCResponse


class _TestRPCRequest(RPCRequest):

    def serialize(self):
        return


class _TestRPCResponse(RPCResponse):
    pass


class _TestRPCProtocol(RPCProtocol):

    def create_request(self, method, args=None, kwargs=None, one_way=False):
        return _TestRPCRequest()

    def parse_reply(self, data):
        response = _TestRPCResponse()
        response.result = data
        return response


class _TestClientTransport(ClientTransport):

    def send_message(self, message, expect_reply=True):
        if expect_reply:
            return 'test'


class _TestRPCClient(RPCClient):

    def __init__(self):
        super(_TestRPCClient, self).__init__(
            _TestRPCProtocol(),
            _TestClientTransport(),
        )


class Test_Client(unittest.TestCase):

    def test_one_way(self):
        client = _TestRPCClient()
        proxy = client.get_proxy(one_way=True)
        response = proxy.execute()
        assert response is None

    def test_two_way(self):
        client = _TestRPCClient()
        proxy = client.get_proxy(one_way=False)
        response = proxy.execute()
        assert response == 'test'

if __name__ == '__main__':
    unittest.main()
