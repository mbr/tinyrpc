#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol


@pytest.fixture(params=['jsonrpc'])
def protocol(request):
    if 'jsonrpc':
        return JSONRPCProtocol()

    raise RuntimeError('Bad protocol name in test case')


def test_protocol_returns_strings(protocol):
    req = protocol.create_request('foo', ['bar'])

    assert isinstance(req.serialize(), str)

def test_procotol_responds_strings(protocol):
    req = protocol.create_request('foo', ['bar'])
    rep = req.respond(42)
    err_rep = req.error_respond(Exception('foo'))

    assert isinstance(rep.serialize(), str)
    assert isinstance(err_rep.serialize(), str)
