#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import Mock

from tinyrpc.exc import RPCError
from tinyrpc.client import RPCClient, RPCProxy
from tinyrpc.protocols import RPCProtocol, RPCResponse, RPCErrorResponse, RPCRequest
from tinyrpc.transports import ClientTransport


@pytest.fixture(params=['test_method1', 'method2', 'CamelCasedMethod'])
def method_name(request):
    return request.param


@pytest.fixture(params=[(), ('foo', None, 42), (1, )])
def method_args(request):
    return request.param


@pytest.fixture(
    params=[(), (('foo', 'bar'), ('x', None), ('y', 42)), (('q', 1), )]
)
def method_kwargs(request):
    return dict(request.param or {})


@pytest.fixture(params=['', 'NoDot', 'dot.'])
def prefix(request):
    return request.param


@pytest.fixture(params=[True, False])
def one_way_setting(request):
    return request.param


@pytest.fixture
def mock_client():
    return Mock(RPCClient)


@pytest.fixture
def mock_protocol():
    mproto = Mock(RPCProtocol)

    foo = Mock(RPCResponse)
    foo.result = None

    mproto.parse_reply = Mock(return_value=foo)

    return mproto


@pytest.fixture
def mock_transport():
    return Mock(ClientTransport)


@pytest.fixture()
def client(mock_protocol, mock_transport):
    return RPCClient(mock_protocol, mock_transport)


@pytest.fixture
def m_proxy(mock_client, prefix, one_way_setting):
    return RPCProxy(mock_client, prefix, one_way_setting)


def test_proxy_calls_correct_method(
        m_proxy, mock_client, prefix, method_kwargs, method_args, method_name,
        one_way_setting
):

    getattr(m_proxy, method_name)(*method_args, **method_kwargs)

    mock_client.call.assert_called_with(
        prefix + method_name,
        method_args,
        method_kwargs,
        one_way=one_way_setting
    )


def test_client_uses_correct_protocol(
        client, mock_protocol, method_name, method_args, method_kwargs,
        one_way_setting
):
    client.call(method_name, method_args, method_kwargs, one_way_setting)

    assert mock_protocol.create_request.called


def test_client_uses_correct_transport(
        client, mock_protocol, method_name, method_args, method_kwargs,
        one_way_setting, mock_transport
):
    client.call(method_name, method_args, method_kwargs, one_way_setting)
    assert mock_transport.send_message.called


def test_client_passes_correct_reply(
        client, mock_protocol, method_name, method_args, method_kwargs,
        one_way_setting, mock_transport
):
    transport_return = '023hoisdfh'
    mock_transport.send_message = Mock(return_value=transport_return)
    client.call(method_name, method_args, method_kwargs, one_way_setting)
    if one_way_setting:
        mock_protocol.parse_reply.assert_not_called()
    else:
        mock_protocol.parse_reply.assert_called_with(transport_return)


def test_client_raises_error_replies(
        client, mock_protocol, method_name, method_args, method_kwargs,
        one_way_setting
):
    error_response = RPCErrorResponse()
    error_response.error = 'foo'
    mock_protocol.parse_reply = Mock(return_value=error_response)

    if not one_way_setting:
        client.call(method_name, method_args, method_kwargs, one_way_setting)
        mock_protocol.raise_error.assert_called_with('foo')


def test_client_raises_indirect_error_replies(
        client, mock_protocol, method_name, method_args, method_kwargs,
        one_way_setting
):
    class MockException(Exception):
        pass

    def raise_error(error):
        raise MockException(error)

    error_response = RPCErrorResponse()
    error_response.error = 'foo'
    mock_protocol.parse_reply = Mock(return_value=error_response)
    mock_protocol.raise_error = raise_error

    if not one_way_setting:
        with pytest.raises(MockException):
            client.call(
                method_name, method_args, method_kwargs, one_way_setting
            )


def test_client_produces_good_proxy(client, prefix, one_way_setting):
    proxy = client.get_proxy(prefix, one_way_setting)
    assert proxy.client == client
    assert proxy.prefix == prefix
    assert proxy.one_way == one_way_setting
    assert callable(proxy.foobar)


@pytest.mark.skip(
    'no longer performs automatic conversion, serialize() always returns bytes'
)
def test_client_send_binary_message(
        client, mock_protocol, method_name, method_args, method_kwargs,
        one_way_setting, mock_transport
):
    req = Mock(RPCRequest)
    req.serialize.return_value = u'unicode not acceptable'
    mock_protocol.create_request.return_value = req
    client.call(method_name, method_args, method_kwargs, one_way_setting)
    assert mock_transport.send_message.called
    assert isinstance(mock_transport.send_message.call_args[0][0], bytes)
