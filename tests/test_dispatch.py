#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mock import Mock, MagicMock
import pytest

from tinyrpc.dispatch import RPCDispatcher, public
from tinyrpc import RPCRequest, RPCBatchRequest, RPCBatchResponse


@pytest.fixture
def dispatch():
    return RPCDispatcher()


@pytest.fixture()
def subdispatch():
    return RPCDispatcher()


@pytest.fixture()
def mock_request(method='subtract', args=None, kwargs=None):
    mock_request = Mock(RPCRequest)
    mock_request.method = method
    mock_request.args = args or [4, 6]
    mock_request.kwargs = kwargs or {}
    mock_request.respond = Mock(RPCRequest.respond)
    mock_request.error_respond = Mock(RPCRequest.error_respond)

    return mock_request


def test_function_decorating_without_paramters(dispatch):
    @dispatch.public
    def foo(bar):
        pass

    assert dispatch.get_method('foo') == foo


def test_function_decorating_with_empty_paramters(dispatch):
    @dispatch.public()
    def foo(bar):
        pass

    assert dispatch.get_method('foo') == foo


def test_function_decorating_with_paramters(dispatch):
    @dispatch.public(name='baz')
    def foo(bar):
        pass

    with pytest.raises(KeyError):
        dispatch.get_method('foo')


    assert dispatch.get_method('baz') == foo


def test_subdispatchers(dispatch, subdispatch):
    @dispatch.public()
    def foo(bar):
        pass

    @subdispatch.public(name='foo')
    def subfoo(bar):
        pass

    dispatch.add_subdispatch(subdispatch, 'sub.')

    assert dispatch.get_method('foo') == foo
    assert dispatch.get_method('sub.foo') == subfoo


def test_object_method_marking():
    class Foo(object):
        def foo1(self):
            pass

        @public
        def foo2(self):
            pass

        @public(name='baz')
        def foo3(self):
            pass

    f = Foo()

    assert not hasattr(f.foo1, '_rpc_public_name')
    assert f.foo2._rpc_public_name == 'foo2'
    assert f.foo3._rpc_public_name == 'baz'


def test_object_method_register(dispatch):
    class Foo(object):
        def foo1(self):
            pass

        @public
        def foo2(self):
            pass

        @public(name='baz')
        def foo3(self):
            pass

    f = Foo()
    dispatch.register_instance(f)

    with pytest.raises(KeyError):
        assert dispatch.get_method('foo1')

    assert dispatch.get_method('foo2') == f.foo2
    assert dispatch.get_method('baz') == f.foo3


def test_object_method_register_with_prefix(dispatch):
    class Foo(object):
        def foo1(self):
            pass

        @public
        def foo2(self):
            pass

        @public(name='baz')
        def foo3(self):
            pass

    f = Foo()
    dispatch.register_instance(f, 'myprefix')

    with pytest.raises(KeyError):
        assert dispatch.get_method('foo1')

    with pytest.raises(KeyError):
        assert dispatch.get_method('myprefixfoo1')

    with pytest.raises(KeyError):
        assert dispatch.get_method('foo2')

    with pytest.raises(KeyError):
        assert dispatch.get_method('foo3')

    assert dispatch.get_method('myprefixfoo2') == f.foo2
    assert dispatch.get_method('myprefixbaz') == f.foo3


def test_dispatch_calls_method_and_responds(dispatch, mock_request):
    m = Mock()
    m.subtract = Mock(return_value=-2)

    dispatch.add_method(m.subtract, 'subtract')
    response = dispatch.dispatch(mock_request)

    m.subtract.assert_called()

    mock_request.respond.assert_called_with(-2)


def test_dispatch_handles_in_function_exceptions(dispatch, mock_request):
    m = Mock()
    m.subtract = Mock(return_value=-2)

    class MockError(Exception):
        pass

    m.subtract.side_effect = MockError('mock error')

    dispatch.add_method(m.subtract, 'subtract')
    response = dispatch.dispatch(mock_request)

    m.subtract.assert_called()

    mock_request.error_respond.assert_called_with(m.subtract.side_effect)


def test_batch_dispatch(dispatch):
    method1 = Mock(return_value='rv1')
    method2 = Mock(return_value=None)

    dispatch.add_method(method1, 'method1')
    dispatch.add_method(method2, 'method2')

    batch_request = RPCBatchRequest()
    batch_request.error_respond = Mock(return_value='ERROR')
    batch_request.append(mock_request('method1', args=[1,2]))
    batch_request.append(mock_request('non_existant_method', args=[5,6]))
    batch_request.append(mock_request('method2', args=[3,4]))

    batch_request.create_batch_response = lambda: RPCBatchResponse()

    assert batch_request.error_respond.call_count == 0

    response = dispatch.dispatch(batch_request)

    # assert all methods are called
    method1.assert_called_with(1, 2)
    method2.assert_called_with(3, 4)

    # FIXME: could use better checking?


def test_dispatch_raises_key_error(dispatch):
    with pytest.raises(KeyError):
        dispatch.get_method('foo')
