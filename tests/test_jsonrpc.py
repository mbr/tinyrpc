#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

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

def test_parsing_invalid_json(prot):
    pass

def test_parsing_invalid_arguments(prot):
    pass

def test_batch_request_parsing(prot):
    pass

def test_good_reply_samples(prot):
    pass

def test_proper_construction_of_error_codes(prot):
    pass

def test_notification_yields_None_reply(prot):
    pass
