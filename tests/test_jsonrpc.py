#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import pytest

from tinyrpc import MethodNotFoundError, InvalidRequestError, ServerError, \
                    RPCError
from tinyrpc.protocols.jsonrpc import JSONRPCParseError, \
                                      JSONRPCInvalidRequestError, \
                                      JSONRPCMethodNotFoundError, \
                                      JSONRPCInvalidParamsError, \
                                      JSONRPCInternalError


@pytest.fixture
def prot():
    from tinyrpc.protocols.jsonrpc import JSONRPCProtocol

    return JSONRPCProtocol()


@pytest.mark.parametrize(('data', 'attrs'), [
    # examples from the spec, parsing only
    ("""{"jsonrpc": "2.0", "method": "subtract",
       "params": [42, 23], "id": 1}""",
     {'method': 'subtract', 'args': [42, 23], '_jsonrpc_id': 1}
    ),

    ("""{"jsonrpc": "2.0", "method": "subtract", "params":
        [23, 42], "id": 2}""",
     {'method': 'subtract', 'args': [23, 42], '_jsonrpc_id': 2}
    ),

    ("""{"jsonrpc": "2.0", "method": "subtract", "params":
        {"subtrahend": 23, "minuend": 42}, "id": 3}""",
     {'method': 'subtract', 'kwargs': {'subtrahend': 23, 'minuend': 42},
      '_jsonrpc_id': 3}
    ),

    ("""{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42,
        "subtrahend": 23}, "id": 4}""",
     {'method': 'subtract', 'kwargs': {'minuend': 42, 'subtrahend': 23},
      '_jsonrpc_id': 4},
    ),

    ("""{"jsonrpc": "2.0", "method": "update", "params": [1,2,3,4,5]}""",
     {'method': 'update', 'args': [1, 2, 3, 4, 5]}
    ),

    ("""{"jsonrpc": "2.0", "method": "foobar"}""",
     {'method': 'foobar'}
    ),
])
def test_parsing_good_request_samples(prot, data, attrs):
    req = prot.parse_request(data)

    for k, v in attrs.iteritems():
        assert getattr(req, k) == v


@pytest.mark.parametrize('invalid_json', [
    '{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]',
    'garbage',
])
def test_parsing_invalid_json(prot, invalid_json):
    with pytest.raises(JSONRPCParseError):
        prot.parse_request(invalid_json)


def test_parsing_invalid_arguments(prot):
    with pytest.raises(JSONRPCInvalidParamsError):
        prot.parse_request(
            """{"jsonrpc": "2.0", "method": "update", "params": 9}"""
        )


@pytest.mark.parametrize(('data', 'id', 'result'), [
    ("""{"jsonrpc": "2.0", "result": 19, "id": 1}""",
     1,
     19,
    ),

    ("""{"jsonrpc": "2.0", "result": -19, "id": 2}""",
     2,
     -19,
    ),

    ("""{"jsonrpc": "2.0", "result": 19, "id": 3}""",
     3,
     19,
    ),

    ("""{"jsonrpc": "2.0", "result": 19, "id": 4}""",
     4,
     19,
    ),
])
def test_good_reply_samples(prot, data, id, result):
    reply = prot.parse_reply(data)

    assert reply._jsonrpc_id == id
    assert reply.error == None
    assert reply.rv == result


@pytest.mark.parametrize(('exc', 'code', 'message'), [
    (JSONRPCParseError, -32700, 'Parse error'),
    (JSONRPCInvalidRequestError, -32600, 'Invalid Request'),
    (JSONRPCMethodNotFoundError, -32601, 'Method not found'),
    (JSONRPCInvalidParamsError, -32602, 'Invalid params'),
    (JSONRPCInternalError, -32603, 'Internal error'),

    # generic errors
    (RPCError, -32603, 'Internal error'),
    (Exception, -32603, 'Internal error'),
    (InvalidRequestError, -32600, 'Invalid request'),
    (MethodNotFoundError, -32601, 'Method not found'),
    (ServerError, -32603, 'Internal error'),
])
def test_proper_construction_of_error_codes(prot, exc, code, message):
    reply = prot.create_error_message(exc)

    err = json.loads(reply)

    assert err['code'] == code
    assert err['message'] == message


def test_notification_yields_None_reply(prot):
    data = """{"jsonrpc": "2.0", "method": "update", "params": [1,2,3,4,5]}"""

    req = prot.parse_request(data)

    # updates should never cause retries
    assert req.reply(None, True) == None


def test_batch_empty_array(prot):
    with pytest.raises(JSONRPCInvalidRequestError):
        req.parse_request("""[]""")


def test_batch_invalid_array(prot):
    with pytest.raises(JSONRPCInvalidRequestError):
        req.parse_request("""[1]""")


def test_batch_invalid_batch(prot):
    with pytest.raises(JSONRPCInvalidRequestError):
        req.parse_request("""[1, 2, 3]""")


def test_batch_good_examples(prot):
    data = """
    [
        {"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},
        {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
        {"jsonrpc": "2.0", "method": "subtract", "params": [42,23], "id": "2"},
        {"foo": "boo"},
        {"jsonrpc": "2.0", "method": "foo.get", "params": {"name": "myself"}, "id": "5"},
        {"jsonrpc": "2.0", "method": "get_data", "id": "9"}
    ]
    """

    results = prot.parse_request(data)

    assert isinstance(list, results)
    assert results[0].method == 'sum'
    assert results[0].args == [1, 2, 4]
    assert results[0]._jsonrpc_id == 1

    assert results[1].method == 'notify_hello'
    assert results[1].args == [7]
    assert results[1]._jsonrpc_id == None

    assert results[2].method == 'subtract'
    assert results[2].args == [42, 23]
    assert results[2]._jsonrpc_id == 2

    assert isinstance(JSONRPCInvalidRequestError, results[3])

    assert results[4].method == 'foo.get'
    assert results[4].kwargs == {'name': 'myself'}
    assert results[4]._jsonrpc_id == 5

    assert results[5].method == 'get_data'
    assert results[5].args == None
    assert results[5].kwargs == None
    assert results[5]._jsonrpc_id == 9
