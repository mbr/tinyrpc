#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from mock import Mock

from tinyrpc.client import RPCClient, RPCProxy

@pytest.fixture(params=['test_method1', 'method2', 'CamelCasedMethod'])
def method_name(request):
    return request.param


@pytest.fixture(params=[(), ('foo', None, 42), (1,)])
def method_args(request):
    return request.param


@pytest.fixture(params=[(), (('foo', 'bar'), ('x', None), ('y', 42)),
                        (('q', 1),)])
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
def m_proxy(mock_client, prefix, one_way_setting):
    return RPCProxy(mock_client, prefix, one_way_setting)


def test_proxy_calls_correct_method(m_proxy, mock_client,
                                    prefix, method_kwargs, method_args,
                                    method_name, one_way_setting):

    getattr(m_proxy, method_name)(*method_args, **method_kwargs)

    mock_client.call.assert_called_with(
        prefix + method_name, method_args, method_kwargs,
        one_way=one_way_setting
    )
