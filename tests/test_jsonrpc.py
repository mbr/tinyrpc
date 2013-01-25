#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import pytest

from tinyrpc import MethodNotFoundError, InvalidRequestError, ServerError, \
                    RPCError, RPCSuccessResponse, RPCErrorResponse
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
     {'method': 'subtract', 'args': [42, 23], 'unique_id': 1}
    ),

    ("""{"jsonrpc": "2.0", "method": "subtract", "params":
        [23, 42], "id": 2}""",
     {'method': 'subtract', 'args': [23, 42], 'unique_id': 2}
    ),

    ("""{"jsonrpc": "2.0", "method": "subtract", "params":
        {"subtrahend": 23, "minuend": 42}, "id": 3}""",
     {'method': 'subtract', 'kwargs': {'subtrahend': 23, 'minuend': 42},
      'unique_id': 3}
    ),

    ("""{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42,
        "subtrahend": 23}, "id": 4}""",
     {'method': 'subtract', 'kwargs': {'minuend': 42, 'subtrahend': 23},
      'unique_id': 4},
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

    assert reply.unique_id == id
    assert not reply.is_error
    assert reply.result == result


@pytest.mark.parametrize(('exc', 'code', 'message'), [
    (JSONRPCParseError, -32700, 'Parse error'),
    (JSONRPCInvalidRequestError, -32600, 'Invalid Request'),
    (JSONRPCMethodNotFoundError, -32601, 'Method not found'),
    (JSONRPCInvalidParamsError, -32602, 'Invalid params'),
    (JSONRPCInternalError, -32603, 'Internal error'),

    # generic errors
    (RPCError, -32603, 'Internal error'),
    (Exception, -32603, 'Internal error'),
    (InvalidRequestError, -32600, 'Invalid Request'),
    (MethodNotFoundError, -32601, 'Method not found'),
    (ServerError, -32603, 'Internal error'),
])
def test_proper_construction_of_error_codes(prot, exc, code, message):
    request = prot.parse_request(
        """{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4],
           "id": "1"}"""
    )
    reply = request.error_respond(exc()).serialize()

    err = json.loads(reply)

    assert err['error']['code'] == code
    assert err['error']['message'] == message


def test_notification_yields_None_response(prot):
    data = """{"jsonrpc": "2.0", "method": "update", "params": [1,2,3,4,5]}"""

    req = prot.parse_request(data)

    # updates should never cause retries
    assert req.respond(True) == None


def test_batch_empty_array(prot):
    with pytest.raises(JSONRPCInvalidRequestError):
        prot.parse_request("""[]""")


def test_batch_invalid_array(prot):
    assert isinstance(prot.parse_request("""[1]""")[0],
                      JSONRPCInvalidRequestError)


def test_batch_invalid_batch(prot):
    for r in prot.parse_request("""[1, 2, 3]"""):
        assert isinstance(r, JSONRPCInvalidRequestError)


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

    assert isinstance(results, list)
    assert results[0].method == 'sum'
    assert results[0].args == [1, 2, 4]
    assert results[0].unique_id == "1"

    assert results[1].method == 'notify_hello'
    assert results[1].args == [7]
    assert results[1].unique_id == None

    assert results[2].method == 'subtract'
    assert results[2].args == [42, 23]
    assert results[2].unique_id == "2"

    assert isinstance(results[3], JSONRPCInvalidRequestError)

    assert results[4].method == 'foo.get'
    assert results[4].kwargs == {'name': 'myself'}
    assert results[4].unique_id == "5"

    assert results[5].method == 'get_data'
    assert results[5].args == None
    assert results[5].kwargs == None
    assert results[5].unique_id == "9"

@pytest.mark.parametrize(('exc', 'code', 'message'), [
    (JSONRPCParseError, -32700, 'Parse error'),
    (JSONRPCInvalidRequestError, -32600, 'Invalid Request'),
    (JSONRPCMethodNotFoundError, -32601, 'Method not found'),
    (JSONRPCInvalidParamsError, -32602, 'Invalid params'),
    (JSONRPCInternalError, -32603, 'Internal error'),

    # generic errors
    (RPCError, -32603, 'Internal error'),
    (Exception, -32603, 'Internal error'),
    (InvalidRequestError, -32600, 'Invalid Request'),
    (MethodNotFoundError, -32601, 'Method not found'),
    (ServerError, -32603, 'Internal error'),
])
def test_proper_construction_of_independent_errors(prot, exc, code, message):
    reply = prot.create_error_response(exc()).serialize()

    err = json.loads(reply)

    assert err['error']['code'] == code
    assert err['error']['message'] == message

def test_unique_ids(prot):
    req1 = prot.create_request('foo', [1, 2])
    req2 = prot.create_request('foo', [1, 2])

    assert req1.unique_id != req2.unique_id

def test_one_way(prot):
    req = prot.create_request('foo', None, {'a': 'b'}, True)

    assert req.respond(None) == None

def test_out_of_order(prot):
    req = prot.create_request('foo', ['a', 'b'], None)
    rep = req.respond(1)

    assert req.unique_id == rep.unique_id

def test_raises_on_args_and_kwargs(prot):
    with pytest.raises(Exception):
        prot.create_request('foo', ['arg1', 'arg2'], {'kw_key': 'kw_value'})

def test_supports_no_args(prot):
        prot.create_request('foo')

# FIXME: create_request test-cases
# FIXME: actual mock communication test (full spec?)
