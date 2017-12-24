#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest


import six
import gevent
import gevent.queue
import gevent.monkey
from gevent.pywsgi import WSGIServer
import requests

from tinyrpc.transports.wsgi import WsgiServerTransport
from tinyrpc.transports.http import HttpPostClientTransport

TEST_SERVER_ADDR = ('127.0.0.1', 49294)


@pytest.fixture(scope='module', autouse=True)
def monkey_patches(request):
    # ugh? ugh. ugh. ugh!
    import socket
    gevent.monkey.patch_all(
        socket=True,
        dns=False,
        time=False,
        select=False,
        thread=False,
        os=True,
        httplib=False,
        ssl=False,
        aggressive=False)

    def fin():
        six.moves.reload_module(socket)

    request.addfinalizer(fin)


@pytest.fixture()
def wsgi_server(request):
    app = WsgiServerTransport(queue_class=gevent.queue.Queue)

    server = WSGIServer(TEST_SERVER_ADDR, app.handle)

    def fin():
        server.stop()
        server_greenlet.join()

    request.addfinalizer(fin)
    server_greenlet = gevent.spawn(server.serve_forever)
    gevent.sleep(0)  # wait for server to come up

    return (app, 'http://%s:%d' % TEST_SERVER_ADDR)


def test_server_supports_post_only(wsgi_server):
    transport, addr = wsgi_server

    r = requests.get(addr)

    # we expect a "not supported" response
    assert r.status_code == 405

    r = requests.head(addr)

    # we expect a "not supported" response
    assert r.status_code == 405


@pytest.mark.parametrize(('msg',),
    [(six.b('foo'),), (six.b(''),), (six.b('bar'),), (six.b('1234'),), (six.b('{}'),), (six.b('{'),), (six.b('\x00\r\n'),)])
def test_server_receives_messages(wsgi_server, msg):
    transport, addr = wsgi_server

    def consumer():
        context, received_msg = transport.receive_message()
        assert received_msg == msg
        reply = six.b('reply:') + msg
        transport.send_reply(context, reply)

    gevent.spawn(consumer)

    r = requests.post(addr, data=msg)

    assert r.content == six.b('reply:') + msg


@pytest.fixture
def sessioned_client():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_maxsize=100)
    session.mount('http://', adapter)
    client = HttpPostClientTransport(
        'http://%s:%d' % TEST_SERVER_ADDR,
        post_method=session.post
    )
    return client


@pytest.fixture
def non_sessioned_client():
    client = HttpPostClientTransport('http://%s:%d' % TEST_SERVER_ADDR)
    return client


@pytest.mark.parametrize(('msg',),
    [(six.b('foo'),), (six.b(''),), (six.b('bar'),), (six.b('1234'),), (six.b('{}'),), (six.b('{'),), (six.b('\x00\r\n'),)])
def test_sessioned_http_sessioned_client(wsgi_server, sessioned_client, msg):
    transport, addr = wsgi_server

    def consumer():
        context, received_msg = transport.receive_message()
        assert received_msg == msg
        reply = six.b('reply:') + msg
        transport.send_reply(context, reply)

    gevent.spawn(consumer)

    result = sessioned_client.send_message(msg)
    assert result == six.b('reply:') + msg


def test_exhaust_ports(wsgi_server, non_sessioned_client):
    """
    This raises a
    > ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=49294):
    >    Max retries exceeded with url: / (Caused by
    >    NewConnectionError('<requests.packages.urllib3.connection.HTTPConnection
    >    object at 0x7f6f86246210>: Failed to establish a new connection:
    >    [Errno 99] Cannot assign requested address',))
    """

    transport, addr = wsgi_server

    def consumer():
        context, received_msg = transport.receive_message()
        reply = six.b('reply:') + received_msg
        transport.send_reply(context, reply)

    def send_and_receive(i):
        try:
            gevent.spawn(consumer)
            msg = six.b('msg_%s' % i)
            result = non_sessioned_client.send_message(msg)
            return result == six.b('reply:') + msg
        except Exception as e:
            return e

    pool = gevent.pool.Pool(500)

    with pytest.raises(requests.ConnectionError):
        for result in pool.imap_unordered(send_and_receive, six.moves.xrange(55000)):
            assert result
            if isinstance(result, Exception):
                raise result
