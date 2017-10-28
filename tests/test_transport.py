#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import six

import zmq
import zmq.green

from tinyrpc.transports import ServerTransport, ClientTransport
from tinyrpc.transports.zmq import ZmqServerTransport, ZmqClientTransport


class DummyServerTransport(ServerTransport):
    def __init__(self):
        self.messages = []
        self.clients = {}

    def receive_message(self):
        return self.messages.pop()

    def send_reply(self, context, message):
        if not isinstance(message, sid.string_types):
            raise TypeError('Message must be str().')
        self.clients[context].messages.append(message)


class DummyClientTransport(ClientTransport):
    def __init__(self, server):
        self.server = server
        self.id = id(self)
        self.server.clients[self.id] = self
        self.messages = []

    def send_message(self, message):
        if not isinstance(message, str):
            raise TypeError('Message must be str().')
        self.server.messages.append((self.id, message))

    def receive_reply(self):
        return self.messages.pop()


ZMQ_ENDPOINT = 'inproc://example2'


@pytest.fixture(scope='session')
def zmq_context(request):
    ctx = zmq.Context()
    def fin():
        request.addfinalizer(ctx.destroy())
    return ctx


@pytest.fixture(scope='session')
def zmq_green_context(request):
    ctx = zmq.Context()
    def fin():
        request.addfinalizer(ctx.destroy())
    return ctx


if six.PY3:
    # zmq and zmq.green fail on python3
    SERVERS=['dummy']
else:
    SERVERS=['dummy', 'zmq', 'zmq.green']
@pytest.fixture(params=SERVERS)
def transport(request, zmq_context, zmq_green_context):
    if request.param == 'dummy':
        server = DummyServerTransport()
        client = DummyClientTransport(server)
    elif request.param in ('zmq', 'zmq.green'):
        ctx = zmq_context if request.param == 'zmq' else zmq_green_context

        server = ZmqServerTransport.create(ctx, ZMQ_ENDPOINT)
        client = ZmqClientTransport.create(ctx, ZMQ_ENDPOINT)

        def fin():
            server.socket.close()
            client.socket.close()

        request.addfinalizer(fin)
    else:
        raise ValueError('Invalid transport.')
    return (client, server)

SAMPLE_MESSAGES = ['asdf', 'loremipsum' * 1500, '', '\x00', 'b\x00a', '\r\n',
                   '\n', u'\u1234'.encode('utf8')]
if six.PY3:
    BAD_MESSAGES = [b'asdf', b'', 1234, 1.2, None, True, False, ('foo',)]
else:
    BAD_MESSAGES = [u'asdf', u'', 1234, 1.2, None, True, False, ('foo',)]


@pytest.fixture(scope='session',
                params=SAMPLE_MESSAGES)
def sample_msg(request):
    return request.param


@pytest.fixture(scope='session',
                params=SAMPLE_MESSAGES)
def sample_msg2(request):
    return request.param


@pytest.fixture(scope='session',
                params=BAD_MESSAGES)
def bad_msg(request):
    return request.param

def test_transport_rejects_bad_values(transport, bad_msg):
    client, server = transport
   
    with pytest.raises(TypeError):
        client.send_message(bad_msg)


# FIXME: these tests need to be rethought, as they no longer work properly with
# the change to the interface of ClientTransport

# FIXME: the actual client needs tests as well
