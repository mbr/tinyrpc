#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _compat
from six.moves.mock import Mock, MagicMock
import pytest
import inspect

from tinyrpc.dispatch.async_dispatch import AsyncioRPCDispatcher, public
from tinyrpc import RPCRequest, RPCBatchRequest, RPCBatchResponse
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol, JSONRPCInvalidParamsError
from tinyrpc.exc import *
import asyncio


def create_successful_future(result, loop):
    future = loop.create_future()
    future.set_result(result)
    return future


def create_failed_future(exception, loop):
    future = loop.create_future()
    future.set_exception(exception)
    return future


@pytest.fixture()
def dispatch():
    return AsyncioRPCDispatcher()


@pytest.fixture()
def subdispatch():
    return AsyncioRPCDispatcher()


@pytest.fixture()
def mock_request(method='subtract', args=None, kwargs=None):
    mock_request = Mock(RPCRequest)
    mock_request.method = method
    mock_request.args = args or [4, 6]
    mock_request.kwargs = kwargs or {}

    return mock_request

@pytest.fixture()
def event_loop():
    return asyncio.get_event_loop()



def test_function_decorating_without_parameters(dispatch):
    @dispatch.public
    async def foo(bar):
        pass

    assert dispatch.get_method('foo') == foo


def test_function_decorating_with_empty_parameters(dispatch):
    @dispatch.public()
    async def foo(bar):
        pass

    assert dispatch.get_method('foo') == foo


def test_function_decorating_with_parameters(dispatch):
    @dispatch.public(name='baz')
    async def foo(bar):
        pass

    with pytest.raises(MethodNotFoundError):
        dispatch.get_method('foo')


    assert dispatch.get_method('baz') == foo


def test_subdispatchers(dispatch, subdispatch):
    @dispatch.public()
    async def foo(bar):
        pass

    @subdispatch.public(name='foo')
    async def subfoo(bar):
        pass

    dispatch.add_subdispatch(subdispatch, 'sub.')

    assert dispatch.get_method('foo') == foo
    assert dispatch.get_method('sub.foo') == subfoo


def test_object_method_marking():
    class Foo(object):
        async def foo1(self):
            pass

        @public
        async def foo2(self):
            pass

        @public(name='baz')
        async def foo3(self):
            pass

    f = Foo()

    assert not hasattr(f.foo1, '_rpc_public_name')
    assert f.foo2._rpc_public_name == 'foo2'
    assert f.foo3._rpc_public_name == 'baz'


def test_object_method_register(dispatch):
    class Foo(object):
        async def foo1(self):
            pass

        @public
        async def foo2(self):
            pass

        @public(name='baz')
        async def foo3(self):
            pass

    f = Foo()
    dispatch.register_instance(f)

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('foo1')

    assert dispatch.get_method('foo2') == f.foo2
    assert dispatch.get_method('baz') == f.foo3


def test_object_method_register_with_prefix(dispatch):
    class Foo(object):
        async def foo1(self):
            pass

        @public
        async def foo2(self):
            pass

        @public(name='baz')
        async def foo3(self):
            pass

    f = Foo()
    dispatch.register_instance(f, 'myprefix')

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('foo1')

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('myprefixfoo1')

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('foo2')

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('foo3')

    assert dispatch.get_method('myprefixfoo2') == f.foo2
    assert dispatch.get_method('myprefixbaz') == f.foo3


def test_dispatch_calls_method_and_responds(dispatch, mock_request, event_loop):
    m = Mock()
    future = create_successful_future(-2, event_loop)
    m.subtract = Mock(return_value=future)

    dispatch.add_method(m.subtract, 'subtract')
    response = event_loop.run_until_complete(dispatch.dispatch(mock_request))

    assert m.subtract.called

    mock_request.respond.assert_called_with(-2)


def test_dispatch_handles_in_function_exceptions(dispatch, mock_request, event_loop):
    m = Mock()
    class MockError(Exception):
        pass
    exception = MockError('mock error')
    future: asyncio.Future = create_failed_future(exception, event_loop)
    #future.set_result(-2)
    m.subtract = Mock(return_value=future)

    dispatch.add_method(m.subtract, 'subtract')
    response = event_loop.run_until_complete(dispatch.dispatch(mock_request))

    assert m.subtract.called
    mock_request.error_respond.assert_called_with(exception)


def test_batch_dispatch(dispatch, event_loop):
    method1 = Mock(return_value=create_successful_future('rv1', event_loop))
    method2 = Mock(return_value=create_successful_future(None, event_loop))

    dispatch.add_method(method1, 'method1')
    dispatch.add_method(method2, 'method2')

    batch_request = RPCBatchRequest()
    batch_request.error_respond = Mock(return_value='ERROR')
    batch_request.append(mock_request('method1', args=[1,2]))
    batch_request.append(mock_request('non_existant_method', args=[5,6]))
    batch_request.append(mock_request('method2', args=[3,4]))

    batch_request.create_batch_response = lambda: RPCBatchResponse()

    assert batch_request.error_respond.call_count == 0

    response = event_loop.run_until_complete(dispatch.dispatch(batch_request))

    # assert all methods are called
    method1.assert_called_with(1, 2)
    method2.assert_called_with(3, 4)

    # FIXME: could use better checking?


def test_dispatch_raises_key_error(dispatch):
    with pytest.raises(MethodNotFoundError):
        dispatch.get_method('foo')

@pytest.fixture(params=[
    ('fn_a', [4, 6], {}, -2),
    ('fn_a', [4], {}, InvalidParamsError),
    # InvalidParamsError instead of JSONRPCInvalidParamsError due to mocking
    ('fn_a', [], {'a':4, 'b':6}, -2),
    ('fn_a', [4], {'b':6}, -2),
    ('fn_b', [4, 6], {}, -2),
    ('fn_b', [], {'a':4, 'b':6}, InvalidParamsError),
    ('fn_b', [4], {}, IndexError),
    # a[1] doesn't exist, can't be detected beforehand
    ('fn_c', [4, 6], {}, InvalidParamsError),
    ('fn_c', [], {'a':4, 'b':6}, -2),
    ('fn_c', [], {'a':4}, KeyError)
    # a['b'] doesn't exist, can't be detected beforehand
])
def invoke_with(request):
    return request.param

def test_argument_error(dispatch, invoke_with, event_loop):
    method, args, kwargs, result = invoke_with

    protocol = JSONRPCProtocol()

    @dispatch.public
    async def fn_a(a, b):
        return a-b

    @dispatch.public
    async def fn_b(*a):
        return a[0]-a[1]

    @dispatch.public
    async def fn_c(**a):
        return a['a']-a['b']

    mock_request = Mock(RPCRequest)
    mock_request.args = args
    mock_request.kwargs = kwargs
    mock_request.method = method
    event_loop.run_until_complete(dispatch._dispatch(mock_request))
    if inspect.isclass(result) and issubclass(result, Exception):
        assert type(mock_request.error_respond.call_args[0][0]) is result
    else:
        mock_request.respond.assert_called_with(result)

def test_call_argument_validation(dispatch):
    def f(a,b):
        return a+b

    dispatch.validate_parameters(f, [1, 2], {})
    with pytest.raises(InvalidParamsError):
        dispatch.validate_parameters(f, [1], {})
    dispatch.validate_parameters(dir, [], {})
    # should skip validation, will produce error otherwise
