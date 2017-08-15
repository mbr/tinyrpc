#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import _compat
from six.moves.mock import Mock, call

from tinyrpc.server import RPCServer
from tinyrpc.transports import ServerTransport
from tinyrpc.protocols import RPCProtocol, RPCResponse
from tinyrpc.dispatch import RPCDispatcher


CONTEXT='sapperdeflap'
RECMSG='out of receive_message'
PARMSG='out of parse_request'
SERMSG='out of serialize'

@pytest.fixture
def transport():
    transport = Mock(ServerTransport)
    transport.receive_message = Mock(return_value=(CONTEXT, RECMSG))
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

@pytest.fixture
def dispatcher(response):
    dispatcher = Mock(RPCDispatcher)
    dispatcher.dispatch = Mock(return_value=response)
    return dispatcher

def test_handle_message(transport, protocol, dispatcher):
    server = RPCServer(transport, protocol, dispatcher)
    server.receive_one_message()
    
    transport.receive_message.assert_called()
    protocol.parse_request.assert_called_with(RECMSG)
    dispatcher.dispatch.assert_called_with(PARMSG, None)
    dispatcher.dispatch().serialize.assert_called()
    transport.send_reply.assert_called_with(CONTEXT, SERMSG)

def test_handle_message_callback(transport, protocol, dispatcher):
    server = RPCServer(transport, protocol, dispatcher)
    server.trace = Mock(return_value=None)
    server.receive_one_message()

    assert server.trace.call_args_list == [call('-->', CONTEXT, RECMSG), call('<--', CONTEXT, SERMSG)]
    server.trace.assert_called()
    