#!/usr/bin/env python
# -*- coding: utf-8 -*-

import msgpack
import pytest

from tinyrpc import InvalidReplyError, MethodNotFoundError
from tinyrpc.protocols.msgpackrpc import (
    MSGPACKRPCParseError,
    MSGPACKRPCInvalidRequestError,
    MSGPACKRPCMethodNotFoundError,
    MSGPACKRPCInvalidParamsError,
    MSGPACKRPCInternalError,
)


def _msgpack_equal(a, b):
    return msgpack.unpackb(a) == msgpack.unpackb(b)


@pytest.fixture
def prot():
    from tinyrpc.protocols.msgpackrpc import MSGPACKRPCProtocol

    return MSGPACKRPCProtocol()


@pytest.mark.parametrize(
    ("data", "attrs"),
    [
        # examples from the JSON-RPC spec, translated to MSGPACK, parsing only
        (
            b"\x94\x00\x01\xa8subtract\x92*\x17",
            {"method": "subtract", "args": [42, 23], "unique_id": 1},
        ),
        (
            b"\x94\x00\x02\xa8subtract\x92\x17*",
            {"method": "subtract", "args": [23, 42], "unique_id": 2},
        ),
        (
            b"\x93\x02\xa6update\x95\x01\x02\x03\x04\x05",
            {"method": "update", "args": [1, 2, 3, 4, 5]},
        ),
        (b"\x93\x02\xa6foobar\x90", {"method": "foobar", "args": []}),
    ],
)
def test_parsing_good_request_samples(prot, data, attrs):
    req = prot.parse_request(data)

    for k, v in attrs.items():
        assert getattr(req, k) == v


@pytest.mark.parametrize(
    "invalid_msgpack",
    [
        b"\x81\xa3\x66\x6f\x6f\xa4\x62\x61\x72",
        b"\x94\x00\x01\x81\xa3aaa\xa3bb",
        b"garbage",
    ],
)
def test_parsing_invalid_msgpack(prot, invalid_msgpack):
    with pytest.raises(MSGPACKRPCParseError):
        prot.parse_request(invalid_msgpack)


@pytest.mark.parametrize(
    "data",
    [
        b"\xc0",  # None
        b"\x94\x00\xc0\xa3aaa\x90",  # [0, None, "aaa", []] - request ID not int
        b"\x95\x00\x02\xa3aaa\x90\xc0",  # [0, 2, "aaa", [], None] - too long
        b"\x94\x02\xa3aaa\x90\xc0",  # [2, "aaa", [], None] - too long
        b"\x93\x02\x01\x90",  # [2, 1, []] - method name not string
    ],
)
def test_parsing_valid_msgpack_but_invalid_rpc_message(prot, data):
    with pytest.raises(MSGPACKRPCInvalidRequestError):
        prot.parse_request(data)


@pytest.mark.parametrize(
    "invalid_args",
    [
        b"\x94\x00\x03\xa6update\t",  # [0, 3, "update", 9]
        b"\x94\x00\x03\xa6foobar\xc0",  # [0, 3, "foobar", None]
        b"\x93\x02\xa3aaa\xc0",  # [2, "aaa", None]
    ],
)
def test_parsing_invalid_arguments(prot, invalid_args):
    with pytest.raises(MSGPACKRPCInvalidParamsError):
        prot.parse_request(invalid_args)


@pytest.mark.parametrize(
    ("data", "id", "result"),
    [
        (b"\x94\x01\x01\xc0\x13", 1, 19),  # [1, 1, None, 19]
        (b"\x94\x01\x02\xc0\xed", 2, -19),  # [1, 2, None, -19]
        (b"\x94\x01\x03\xc0\x13", 3, 19),  # [1, 3, None, 19]
        (b"\x94\x01\x04\xc0\x13", 4, 19),  # [1, 4, None, 19]
    ],
)
def test_good_reply_samples(prot, data, id, result):
    reply = prot.parse_reply(data)

    assert reply.unique_id == id
    assert reply.result == result


@pytest.mark.parametrize(
    ("data", "id", "code", "message"),
    [
        # Neovim-style
        (b"\x94\x01\x05\x92\xcd\x04\xd2\xa5Error\xc0", 5, 1234, "Error"),
        # Ordinary error string
        (b"\x94\x01\x05\xa5Error\xc0", 5, None, "Error"),
        # Two-item list but the types don't match Neovim's style
        (b"\x94\x01\x05\x92\xa41234\xa5Error\xc0", 5, None, ["1234", "Error"]),
    ],
)
def test_good_error_reply_samples(prot, data, id, code, message):
    reply = prot.parse_reply(data)

    assert reply.unique_id == id
    assert reply._msgpackrpc_error_code == code
    assert reply.error == message


@pytest.mark.parametrize(
    ("exc", "code", "message"),
    [
        (MSGPACKRPCParseError, -32700, "Parse error"),
        (MSGPACKRPCInvalidRequestError, -32600, "Invalid request"),
        (MSGPACKRPCMethodNotFoundError, -32601, "Method not found"),
        (MSGPACKRPCInvalidParamsError, -32602, "Invalid params"),
        (MSGPACKRPCInternalError, -32603, "Internal error"),
    ],
)
def test_proper_construction_of_error_codes(prot, exc, code, message):
    reply = exc().error_respond().serialize()
    assert isinstance(reply, bytes)

    err = msgpack.unpackb(reply, raw=False)

    assert err[0] == 1
    assert err[2] == [code, message]


def test_notification_yields_None_response(prot):
    # [2, "update", [1,2,3,4,5]]
    data = b"\x93\x02\xa6update\x95\x01\x02\x03\x04\x05"

    req = prot.parse_request(data)

    assert req.one_way is True

    # updates should never cause retries
    assert req.respond(True) is None


@pytest.mark.parametrize(
    "data",
    [
        b"\x90",  # \x90 = []
        b"\x91\x01",  # \x91\x01 = [1]
        b"\x93\x01\x02\x03",  # \x93\x01\x02\x03 = [1, 2, 3]
        (
            b"\x95\x94\x00\x01\xa3sum\x93\x01\x02\x04"
            b"\x93\x02\xacnotify_hello\x91\x07"
            b"\x94\x00\x02\xa8subtract\x92*\x17"
            b"\x94\x00\x05\xa7foo.get\x81\xa4name\xa6myself"
            b"\x94\x00\t\xa8get_data\xc0"
        ),
    ],
)
def test_batch_examples(prot, data):
    with pytest.raises(MSGPACKRPCInvalidRequestError):
        prot.parse_request(data)


def test_unique_ids(prot):
    req1 = prot.create_request("foo", [1, 2])
    req2 = prot.create_request("foo", [1, 2])

    assert req1.unique_id != req2.unique_id


def test_out_of_order(prot):
    req = prot.create_request("foo", ["a", "b"], None)
    rep = req.respond(1)

    assert req.unique_id == rep.unique_id


def test_request_generation(prot):
    data = msgpack.unpackb(
        prot.create_request("subtract", [42, 23]).serialize(), raw=False
    )

    assert data[0] == 0
    assert isinstance(data[1], int)
    assert data[2] == "subtract"
    assert data[3] == [42, 23]


# The tests below are adapted from the JSON-RPC specification, hence their names


def test_jsonrpc_spec_v2_example1(prot):
    # reset id counter
    from tinyrpc.protocols import default_id_generator
    prot._id_generator = default_id_generator(1)

    request = prot.create_request("subtract", [42, 23])

    assert request.serialize() == b"\x94\x00\x01\xa8subtract\x92*\x17"

    reply = request.respond(19)

    assert reply.serialize() == b"\x94\x01\x01\xc0\x13"

    request = prot.create_request("subtract", [23, 42])

    assert request.serialize() == b"\x94\x00\x02\xa8subtract\x92\x17*"

    reply = request.respond(-19)

    assert reply.serialize() == b"\x94\x01\x02\xc0\xed"


def test_jsonrpc_spec_v2_example3(prot):
    request = prot.create_request("update", [1, 2, 3, 4, 5], one_way=True)

    assert request.serialize() == b"\x93\x02\xa6update\x95\x01\x02\x03\x04\x05"

    request = prot.create_request("foobar", one_way=True)

    assert request.serialize() == b"\x93\x02\xa6foobar\x90"


def test_jsonrpc_spec_v2_example4(prot):
    request = prot.create_request("foobar")
    request.unique_id = 1

    assert request.serialize() == b"\x94\x00\x01\xa6foobar\x90"

    response = request.error_respond(MethodNotFoundError("foobar"))

    assert _msgpack_equal(
        b"\x94\x01\x01\x92\xd1\x80\xa7\xb0Method not found\xc0", response.serialize()
    )


def test_jsonrpc_spec_v2_example5(prot):
    try:
        prot.parse_request(b"\x94\x00\x01\x81\xa3aaa\xa3bb")
        assert False  # parsing must fail
    except MSGPACKRPCParseError as error:
        e = error

    response = e.error_respond()

    # TODO(ntamas): here we are sending None as the request ID because
    # obviously we could not parse it from a malformed request. We need to
    # decide whether this is valid MSGPACK or not.
    assert _msgpack_equal(
        b"\x94\x01\xc0\x92\xd1\x80D\xabParse error\xc0", response.serialize()
    )


def test_jsonrpc_spec_v2_example6(prot):
    try:
        prot.parse_request(b"\x94\x00\x01\x01\xa3bar")
        assert False  # parsing must fail
    except MSGPACKRPCInvalidRequestError as error:
        e = error

    response = e.error_respond()

    assert _msgpack_equal(
        b"\x94\x01\x01\x92\xd1\x80\xa8\xafInvalid request\xc0", response.serialize()
    )


def test_jsonrpc_spec_v2_example8(prot):
    try:
        prot.parse_request(b"\x90")
        assert False
    except MSGPACKRPCInvalidRequestError as error:
        e = error

    response = e.error_respond()

    assert _msgpack_equal(
        b"\x94\x01\xc0\x92\xd1\x80\xa8\xafInvalid request\xc0", response.serialize()
    )


def test_jsonrpc_spec_v2_example9(prot):
    try:
        prot.parse_request(b"\x91\x01")
        assert False
    except MSGPACKRPCInvalidRequestError as error:
        e = error

    response = e.error_respond()

    assert _msgpack_equal(
        b"\x94\x01\xc0\x92\xd1\x80\xa8\xafInvalid request\xc0", response.serialize()
    )


def test_jsonrpc_spec_v2_example10(prot):
    try:
        prot.parse_request(b"\x93\x01\x02\x03")
        assert False
    except MSGPACKRPCInvalidRequestError as error:
        e = error

    response = e.error_respond()

    assert _msgpack_equal(
        b"\x94\x01\xc0\x92\xd1\x80\xa8\xafInvalid request\xc0", response.serialize()
    )


def test_jsonrpc_spec_v2_example11(prot):
    # Since MSGPACK does not support batched request, we test the requests
    # one by one
    requests = []

    for data in [
        b"\x94\x00\x01\xa3sum\x93\x01\x02\x04",  # [0, 1, "sum", [1,2,4]]
        b"\x93\x02\xacnotify_hello\x91\x07",  # [2, "notify_hello", [7]
        b"\x94\x00\x02\xa8subtract\x92*\x17",  # [0, 2, "subtract", [42,23]]
        b"\x92\xa3foo\xa3boo",  # ["foo", "boo"]
        b"\x94\x00\x05\xa7foo.get\x92\xa4name\xa6myself",  # [0, 5, "foo.get", ["name", "myself"]]
        b"\x94\x00\t\xa8get_data\x90",  # [0, 9, "get_data", []]
    ]:
        try:
            requests.append(prot.parse_request(data))
        except Exception as ex:
            requests.append(ex)

    assert isinstance(requests[3], MSGPACKRPCInvalidRequestError)

    responses = []
    responses.append(requests[0].respond(7))
    responses.append(requests[1].error_respond(MethodNotFoundError("notify_hello")))
    responses.append(requests[2].respond(19))
    responses.append(requests[3].error_respond())
    responses.append(requests[4].error_respond(MethodNotFoundError("foo.get")))
    responses.append(requests[5].respond(["hello", 5]))

    responses = [
        response.serialize() if response else response for response in responses
    ]

    assert responses[0] == b"\x94\x01\x01\xc0\x07"
    assert responses[1] is None
    assert responses[2] == b"\x94\x01\x02\xc0\x13"
    assert responses[3] == b"\x94\x01\xc0\x92\xd1\x80\xa8\xafInvalid request\xc0"
    assert responses[4] == b"\x94\x01\x05\x92\xd1\x80\xa7\xb0Method not found\xc0"
    assert responses[5] == b"\x94\x01\t\xc0\x92\xa5hello\x05"


def test_can_get_custom_error_messages_out(prot):
    request = prot.create_request("foo")

    custom_msg = "join the army, they said. see the world, they said."

    e = Exception(custom_msg)

    response = request.error_respond(e)

    data = response.serialize()
    assert isinstance(data, bytes)

    decoded = msgpack.unpackb(data, raw=False)

    assert decoded[0] == 1
    assert decoded[1] == request.unique_id
    assert isinstance(decoded[2], list)
    assert decoded[2][1] == custom_msg


def test_accepts_empty_but_not_none_args(prot):
    prot.create_request("foo", args=[])


def test_rejects_nonempty_kwargs(prot):
    with pytest.raises(MSGPACKRPCInvalidRequestError):
        prot.create_request("foo", kwargs={"foo": "bar"})


def test_accepts_empty_kwargs(prot):
    prot.create_request("foo", kwargs={})


@pytest.mark.parametrize(
    "data",
    [
        b"\x97\x01",  # complete garbage
        b"\x93\x01\xc0\xa5hello",  # too short
        b"\x94\x00\x01\xc0\xa5hello",  # not a reply (message type is request)
        b"\x94\x01\xc0\xc0\xa5hello",  # missing message ID in response
        b"\x94\x01\x01\xa5hello\xa5hello",  # contains error _and_ result
    ],
)
def test_invalid_replies(prot, data):
    with pytest.raises(InvalidReplyError):
        prot.parse_reply(data)
