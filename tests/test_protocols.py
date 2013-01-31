#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc import RPCErrorResponse


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


def test_one_way(protocol):
    req = protocol.create_request('foo', None, {'a': 'b'}, True)

    assert req.respond(None) == None


def test_raises_on_args_and_kwargs(protocol):
    with pytest.raises(Exception):
        protocol.create_request('foo', ['arg1', 'arg2'], {'kw_key': 'kw_value'})


def test_supports_no_args(protocol):
        protocol.create_request('foo')


def test_creates_error_response(protocol):
    req = protocol.create_request('foo', ['bar'])
    err_rep = req.error_respond(Exception('foo'))

    assert hasattr(err_rep, 'error')


def test_parses_error_response(protocol):
    req = protocol.create_request('foo', ['bar'])
    err_rep = req.error_respond(Exception('foo'))

    parsed = protocol.parse_reply(err_rep.serialize())

    assert hasattr(parsed, 'error')
