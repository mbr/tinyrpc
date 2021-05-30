#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from unittest.mock import Mock, call

import pytest
from tinyrpc.dispatch import AsyncioRPCDispatcher, RPCDispatcher
from tinyrpc.protocols import RPCProtocol, RPCResponse
from tinyrpc.server import AsyncioRPCServer, RPCServer
from tinyrpc.transports import AsyncioServerTransport, ServerTransport

CONTEXT = 'sapperdeflap'
RECMSG = 'out of receive_message'
PARMSG = 'out of parse_request'
SERMSG = 'out of serialize'


def create_successful_future(result, loop):
    future = loop.create_future()
    future.set_result(result)
    return future


def create_failed_future(exception, loop):
    future = loop.create_future()
    future.set_exception(exception)
    return future


@pytest.fixture
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture
def transport():
    transport = Mock(ServerTransport)
    transport.receive_message = Mock(return_value=(CONTEXT, RECMSG))
    return transport


@pytest.fixture
def async_transport(event_loop):
    transport = Mock(AsyncioServerTransport)
    future = create_successful_future((CONTEXT, RECMSG), event_loop)
    transport.receive_message = Mock(return_value=future)
    return transport


@pytest.fixture
def protocol():
    protocol = Mock(RPCProtocol)
    protocol.parse_request = Mock(return_value=PARMSG)
    return protocol


@pytest.fixture()
def response():
    response = Mock(RPCResponse)
    response.serialize = Mock(return_value=SERMSG)
    return response


@pytest.fixture()
def async_response(event_loop):
    response = Mock(RPCResponse)
    future = create_successful_future(SERMSG, event_loop)
    response.serialize = Mock(return_value=future)
    return response


@pytest.fixture
def dispatcher(response):
    dispatcher = Mock(RPCDispatcher)
    dispatcher.dispatch = Mock(return_value=response)
    return dispatcher


@pytest.fixture
def async_dispatcher(async_response):
    dispatcher = AsyncioRPCDispatcher()
    dispatcher.dispatch = Mock(dispatcher.dispatch, return_value=async_response)
    return dispatcher


def test_handle_message(transport, protocol, dispatcher):
    server = RPCServer(transport, protocol, dispatcher)
    server.receive_one_message()

    transport.receive_message.assert_called()
    protocol.parse_request.assert_called_with(RECMSG)
    dispatcher.dispatch.assert_called_with(PARMSG, None)
    dispatcher.dispatch().serialize.assert_called()
    transport.send_reply.assert_called_with(CONTEXT, SERMSG)


def test_async_handle_message(async_transport, protocol, async_dispatcher,
                              event_loop):
    server = AsyncioRPCServer(async_transport, protocol, async_dispatcher)
    event_loop.run_until_complete(server.receive_one_message())

    async_transport.receive_message.assert_called()
    protocol.parse_request.assert_called_with(RECMSG)
    print(async_dispatcher.dispatch.call_args)
    async_dispatcher.dispatch.assert_called_with(PARMSG, None)
    #async_dispatcher.dispatch().serialize.assert_called()
    a,b = async_transport.send_reply.call_args[0]
    assert (a,b.result()) == (CONTEXT, SERMSG)


def test_handle_message_callback(transport, protocol, dispatcher):
    server = RPCServer(transport, protocol, dispatcher)
    server.trace = Mock(return_value=None)
    server.receive_one_message()

    assert server.trace.call_args_list == [call('-->', CONTEXT, RECMSG), call('<--', CONTEXT, SERMSG)]
    server.trace.assert_called()


def test_async_handle_message_callback(async_transport, protocol, async_dispatcher, event_loop):
    server = AsyncioRPCServer(async_transport, protocol, async_dispatcher)
    server.trace = Mock(return_value=None)
    event_loop.run_until_complete(server.receive_one_message())

    server.trace.assert_called()
    call_args = server.trace.call_args_list
    assert len(call_args) == 2
    assert call_args[0][0] == ('-->', CONTEXT, RECMSG)
    a,b,c = call_args[1][0]
    assert (a,b,c.result()) == ('<--', CONTEXT, SERMSG)
