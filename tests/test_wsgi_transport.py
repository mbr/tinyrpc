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

TEST_SERVER_ADDR = ('127.0.0.1', 49294)


@pytest.fixture(scope='module', autouse=True)
def monkey_patches(request):
    # ugh? ugh. ugh. ugh!
    import socket
#    if six.PY2:
#        import httplib
#    else:
#        import http.client as httplib

    # FIXME: httplib=True has been removed in more recent gevent versions
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
#        six.moves.reload_module(httplib)

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


@pytest.mark.skipif(six.PY3, reason='Somehow fails on PY3')
@pytest.mark.parametrize(('msg',),
    [('foo',), ('',), ('bar',), ('1234',), ('{}',), ('{',), ('\x00\r\n',)])
def test_server_receives_messages(wsgi_server, msg):
    transport, addr = wsgi_server

    def consumer():
        context, received_msg = transport.receive_message()
        assert received_msg == msg
        reply = 'reply:' + msg
        transport.send_reply(context, reply)

    gevent.spawn(consumer)

    r = requests.post(addr, data=msg)

    assert r.content == 'reply:' + msg
