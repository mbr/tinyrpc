#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import Mock
import pytest
import inspect

from tinyrpc.dispatch import RPCDispatcher, AsyncioRPCDispatcher, public
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


@pytest.fixture
def dispatch():
    return RPCDispatcher()


@pytest.fixture
def async_dispatch():
    return AsyncioRPCDispatcher()


@pytest.fixture
def subdispatch():
    return RPCDispatcher()


@pytest.fixture
def async_subdispatch():
    return AsyncioRPCDispatcher()


def mock_request(method='subtract', args=None, kwargs=None):
    mock_request = Mock(RPCRequest)
    mock_request.method = method
    mock_request.args = args or [4, 6]
    mock_request.kwargs = kwargs or {}

    return mock_request


@pytest.fixture(name="mock_request")
def mock_request_fixture():
    return mock_request()


@pytest.fixture
def event_loop():
    return asyncio.get_event_loop()


def test_function_decorating_without_parameters(dispatch):
    @dispatch.public
    def foo(bar):
        pass

    assert dispatch.get_method('foo') == foo


def test_async_function_decorating_without_parameters(async_dispatch):
    @async_dispatch.public
    async def foo(bar):
        pass

    assert async_dispatch.get_method('foo') == foo


def test_sync_function_in_async_dispatcher(async_dispatch):
    @async_dispatch.public
    def foo(bar):
        pass

    assert async_dispatch.get_method('foo') == foo


def test_function_decorating_with_empty_parameters(dispatch):
    @dispatch.public()
    def foo(bar):
        pass

    assert dispatch.get_method('foo') == foo


def test_async_function_decorating_with_empty_parameters(async_dispatch):
    @async_dispatch.public()
    async def foo(bar):
        pass

    assert async_dispatch.get_method('foo') == foo


def test_function_decorating_with_parameters(dispatch):
    @dispatch.public(name='baz')
    def foo(bar):
        pass

    with pytest.raises(MethodNotFoundError):
        dispatch.get_method('foo')


    assert dispatch.get_method('baz') == foo


def test_async_function_decorating_with_parameters(async_dispatch):
    @async_dispatch.public(name='baz')
    def foo(bar):
        pass

    with pytest.raises(MethodNotFoundError):
        async_dispatch.get_method('foo')
    
    assert async_dispatch.get_method('baz') == foo


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


def test_async_subdispatchers(async_dispatch, async_subdispatch):
    @async_dispatch.public()
    def foo(bar):
        pass

    @async_subdispatch.public(name='foo')
    def subfoo(bar):
        pass

    async_dispatch.add_subdispatch(async_subdispatch, 'sub.')

    assert async_dispatch.get_method('foo') == foo
    assert async_dispatch.get_method('sub.foo') == subfoo

    
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


def test_async_object_method_marking():
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

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('foo1')

    assert dispatch.get_method('foo2') == f.foo2
    assert dispatch.get_method('baz') == f.foo3


def test_async_object_method_register(async_dispatch):
    class Foo(object):
        async def foo1(self):
            pass

        @public
        def foo2(self):
            pass

        @public(name='baz')
        def foo3(self):
            pass

    f = Foo()
    async_dispatch.register_instance(f)

    with pytest.raises(MethodNotFoundError):
        assert async_dispatch.get_method('foo1')

    assert async_dispatch.get_method('foo2') == f.foo2
    assert async_dispatch.get_method('baz') == f.foo3


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


def test_async_object_method_register_with_prefix(async_dispatch):
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
    async_dispatch.register_instance(f, 'myprefix')

    with pytest.raises(MethodNotFoundError):
        assert async_dispatch.get_method('foo1')

    with pytest.raises(MethodNotFoundError):
        assert async_dispatch.get_method('myprefixfoo1')

    with pytest.raises(MethodNotFoundError):
        assert async_dispatch.get_method('foo2')
    
    with pytest.raises(MethodNotFoundError):
        assert async_dispatch.get_method('foo3')
    
    assert async_dispatch.get_method('myprefixfoo2') == f.foo2
    assert async_dispatch.get_method('myprefixbaz') == f.foo3


def test_dispatch_calls_method_and_responds(dispatch, mock_request):
    m = Mock()
    m.subtract = Mock(return_value=-2)

    dispatch.add_method(m.subtract, 'subtract')
    response = dispatch.dispatch(mock_request)

    assert m.subtract.called

    mock_request.respond.assert_called_with(-2)


def test_async_dispatch_calls_method_and_responds(async_dispatch, mock_request, event_loop):
    m = Mock()
    future = create_successful_future(-2, event_loop)
    m.subtract = Mock(return_value=future)

    async_dispatch.add_method(m.subtract, 'subtract')
    response = event_loop.run_until_complete(async_dispatch.dispatch(mock_request))

    assert m.subtract.called

    mock_request.respond.assert_called_with(-2)


def test_async_dispatch_sync_calls_method_and_responds(async_dispatch, mock_request, event_loop):
    m = Mock()
    m.subtract = Mock(return_value=-2)

    async_dispatch.add_method(m.subtract, 'subtract')
    response = event_loop.run_until_complete(async_dispatch.dispatch(mock_request))

    assert m.subtract.called

    mock_request.respond.assert_called_with(-2)


def test_dispatch_handles_in_function_exceptions(dispatch, mock_request):
    m = Mock()
    m.subtract = Mock(return_value=-2)

    class MockError(Exception):
        pass

    m.subtract.side_effect = MockError('mock error')

    dispatch.add_method(m.subtract, 'subtract')
    response = dispatch.dispatch(mock_request)

    assert m.subtract.called

    mock_request.error_respond.assert_called_with(m.subtract.side_effect)


def test_async_dispatch_handles_in_function_exceptions(async_dispatch, mock_request, event_loop):
    m = Mock()

    class MockError(Exception):
        pass

    exception = MockError('mock error')
    future: asyncio.Future = create_failed_future(exception, event_loop)
    #future.set_result(-2)
    m.subtract = Mock(return_value=future)

    async_dispatch.add_method(m.subtract, 'subtract')
    response = event_loop.run_until_complete(async_dispatch.dispatch(mock_request))

    assert m.subtract.called
    mock_request.error_respond.assert_called_with(exception)


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


def test_async_batch_dispatch(async_dispatch, event_loop):
    method1 = Mock(return_value=create_successful_future('rv1', event_loop))
    method2 = Mock(return_value=create_successful_future(None, event_loop))

    async_dispatch.add_method(method1, 'method1')
    async_dispatch.add_method(method2, 'method2')

    batch_request = RPCBatchRequest()
    batch_request.error_respond = Mock(return_value='ERROR')
    batch_request.append(mock_request('method1', args=[1,2]))
    batch_request.append(mock_request('non_existant_method', args=[5,6]))
    batch_request.append(mock_request('method2', args=[3,4]))

    batch_request.create_batch_response = lambda: RPCBatchResponse()

    assert batch_request.error_respond.call_count == 0

    response = event_loop.run_until_complete(async_dispatch.dispatch(batch_request))

    # assert all methods are called
    method1.assert_called_with(1, 2)
    method2.assert_called_with(3, 4)

    # FIXME: could use better checking?


def test_dispatch_raises_key_error(dispatch):
    with pytest.raises(MethodNotFoundError):
        dispatch.get_method('foo')


def test_async_dispatch_raises_key_error(async_dispatch):
    with pytest.raises(MethodNotFoundError):
        async_dispatch.get_method('foo')


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


def test_argument_error(dispatch, invoke_with):
    method, args, kwargs, result = invoke_with

    protocol = JSONRPCProtocol()

    @dispatch.public
    def fn_a(a, b):
        return a-b

    @dispatch.public
    def fn_b(*a):
        return a[0]-a[1]

    @dispatch.public
    def fn_c(**a):
        return a['a']-a['b']

    mock_request = Mock(RPCRequest)
    mock_request.args = args
    mock_request.kwargs = kwargs
    mock_request.method = method
    dispatch._dispatch(mock_request, getattr(protocol, '_caller', None))
    if inspect.isclass(result) and issubclass(result, Exception):
        assert type(mock_request.error_respond.call_args[0][0]) == result
    else:
        mock_request.respond.assert_called_with(result)


def test_async_argument_error(async_dispatch, invoke_with, event_loop):
    method, args, kwargs, result = invoke_with

    protocol = JSONRPCProtocol()

    @async_dispatch.public
    async def fn_a(a, b):
        return a-b

    @async_dispatch.public
    async def fn_b(*a):
        return a[0]-a[1]
    
    @async_dispatch.public
    async def fn_c(**a):
        return a['a']-a['b']

    mock_request = Mock(RPCRequest)
    mock_request.args = args
    mock_request.kwargs = kwargs
    mock_request.method = method
    event_loop.run_until_complete(async_dispatch._dispatch(mock_request))
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


def test_async_call_argument_validation(async_dispatch):
    def f(a,b):
        return a+b

    async_dispatch.validate_parameters(f, [1, 1], {})
    with pytest.raises(InvalidParamsError):
        async_dispatch.validate_parameters(f, [1], {})
    async_dispatch.validate_parameters(dir, [], {})
    # should skip validation, will produce error otherwise


def test_bound_method_argument_error(dispatch, invoke_with):
    method, args, kwargs, result = invoke_with

    protocol = JSONRPCProtocol()

    class Test:
        c = 0
        @public
        def fn_a(self, a, b):
            return a-b+self.c

        @public
        def fn_b(self, *a):
            return a[0]-a[1]+self.c

        @public
        def fn_c(self, **a):
            return a['a']-a['b']+self.c

    test=Test()
    dispatch.register_instance(test)
    mock_request = Mock(RPCRequest)
    mock_request.args = args
    mock_request.kwargs = kwargs
    mock_request.method = method
    dispatch._dispatch(mock_request, getattr(protocol, '_caller', None))
    if inspect.isclass(result) and issubclass(result, Exception):
        assert type(mock_request.error_respond.call_args[0][0]) == result
    else:
        mock_request.respond.assert_called_with(result)


def test_async_bound_method_argument_error(async_dispatch, invoke_with, event_loop):
    method, args, kwargs, result = invoke_with

    protocol = JSONRPCProtocol()

    class Test:
        c = 0
        @public
        async def fn_a(self, a, b):
            return a-b+self.c
        
        @public
        async def fn_b(self, *a):
            return a[0]-a[1]+self.c

        @public
        async def fn_c(self, **a):
            return a['a']-a['b']+self.c
    
    test = Test()
    async_dispatch.register_instance(test)
    mock_request = Mock(RPCRequest)
    mock_request.args = args
    mock_request.kwargs = kwargs
    mock_request.method = method
    event_loop.run_until_complete(async_dispatch._dispatch(mock_request))
    if inspect.isclass(result) and issubclass(result, Exception):
        assert type(mock_request.error_respond.call_args[0][0]) == result
    else:
        mock_request.respond.assert_called_with(result)


def test_bound_method_validation(dispatch):
    class Test:
        def f(self, a, b):
            return a+b
    inst = Test()

    dispatch.validate_parameters(inst.f, [1, 2], {})
    with pytest.raises(InvalidParamsError):
        dispatch.validate_parameters(inst.f, [1], {})


def test_async_bound_method_validation(async_dispatch):
    class Test:
        async def f(self, a, b):
            return a+b
    inst = Test()

    async_dispatch.validate_parameters(inst.f, [1, 2], {})
    with pytest.raises(InvalidParamsError):
        async_dispatch.validate_parameters(inst.f, [1], {})


def test_unbound_method_argument_error(dispatch, invoke_with):
    method, args, kwargs, result = invoke_with

    protocol = JSONRPCProtocol()

    class Test:
        c = 0
        @public
        def fn_a(a, b):
            return a-b

        @public
        def fn_b(*a):
            return a[0]-a[1]

        @public
        def fn_c(**a):
            return a['a']-a['b']

    dispatch.register_instance(Test)
    mock_request = Mock(RPCRequest)
    mock_request.args = args
    mock_request.kwargs = kwargs
    mock_request.method = method
    dispatch._dispatch(mock_request, getattr(protocol, '_caller', None))
    if inspect.isclass(result) and issubclass(result, Exception):
        assert type(mock_request.error_respond.call_args[0][0]) == result
    else:
        mock_request.respond.assert_called_with(result)


def test_async_unbound_method_argument_error(async_dispatch, invoke_with, event_loop):
    method, args, kwargs, result = invoke_with
    protocol = JSONRPCProtocol()

    class Test:
        c = 0
        @public
        async def fn_a(a, b):
            return a-b
        
        @public
        def fn_b(*a):
            return a[0]-a[1]
        
        @public
        def fn_c(**a):
            return a['a']-a['b']

    async_dispatch.register_instance(Test)
    mock_request = Mock(RPCRequest)
    mock_request.args = args
    mock_request.kwargs = kwargs
    mock_request.method = method
    event_loop.run_until_complete(async_dispatch._dispatch(mock_request))
    if inspect.isclass(result) and issubclass(result, Exception):
        assert type(mock_request.error_respond.call_args[0][0]) == result
    else:
        mock_request.respond.assert_called_with(result)


def test_unbound_method_validation(dispatch):
    class Test:
        def f(a, b):
            return a+b

    dispatch.validate_parameters(Test.f, [1, 2], {})
    with pytest.raises(InvalidParamsError):
        dispatch.validate_parameters(Test.f, [1], {})


def test_async_unbound_method_validation(async_dispatch):
    class Test:
        async def f(a, b):
            return a+b
    
    async_dispatch.validate_parameters(Test.f, [1, 2], {})
    with pytest.raises(InvalidParamsError):
        async_dispatch.validate_parameters(Test.f, [1], {})


def test_static_method_argument_error(dispatch, invoke_with):
    method, args, kwargs, result = invoke_with

    protocol = JSONRPCProtocol()

    class Test:
        c = 0
        @staticmethod
        @public
        def fn_a(a, b):
            return a-b

        @staticmethod
        @public
        def fn_b(*a):
            return a[0]-a[1]

        @staticmethod
        @public
        def fn_c(**a):
            return a['a']-a['b']

    test=Test()
    dispatch.register_instance(test)
    mock_request = Mock(RPCRequest)
    mock_request.args = args
    mock_request.kwargs = kwargs
    mock_request.method = method
    dispatch._dispatch(mock_request, getattr(protocol, '_caller', None))
    if inspect.isclass(result) and issubclass(result, Exception):
        assert type(mock_request.error_respond.call_args[0][0]) == result
    else:
        mock_request.respond.assert_called_with(result)


def test_async_static_method_argument_error(async_dispatch, invoke_with, event_loop):
    method, args, kwargs, result = invoke_with

    protocol = JSONRPCProtocol()

    class Test:
        c = 0
        @staticmethod
        @public
        async def fn_a(a, b):
            return a-b

        @staticmethod
        @public
        async def fn_b(*a):
            return a[0]-a[1]

        @staticmethod
        @public
        async def fn_c(**a):
            return a['a']-a['b']

    test=Test()
    async_dispatch.register_instance(test)
    mock_request = Mock(RPCRequest)
    mock_request.args = args
    mock_request.kwargs = kwargs
    mock_request.method = method
    event_loop.run_until_complete(async_dispatch._dispatch(mock_request))
    if inspect.isclass(result) and issubclass(result, Exception):
        assert type(mock_request.error_respond.call_args[0][0]) == result
    else:
        mock_request.respond.assert_called_with(result)


def test_static_method_validation(dispatch):
    class Test:
        @staticmethod
        def f(a, b):
            return a+b
    inst = Test()

    dispatch.validate_parameters(inst.f, [1, 2], {})
    with pytest.raises(InvalidParamsError):
        dispatch.validate_parameters(inst.f, [1], {})


def test_async_static_method_validation(async_dispatch):
    class Test:
        @staticmethod
        async def f(a, b):
            return a+b
    inst = Test()

    async_dispatch.validate_parameters(inst.f, [1, 2], {})
    with pytest.raises(InvalidParamsError):
        async_dispatch.validate_parameters(inst.f, [1], {})


def test_class_method_argument_error(dispatch, invoke_with):
    method, args, kwargs, result = invoke_with

    protocol = JSONRPCProtocol()

    class Test:
        c = 0
        @classmethod
        @public
        def fn_a(cls, a, b):
            return a-b-cls.c

        @classmethod
        @public
        def fn_b(cls, *a):
            return a[0]-a[1]-cls.c

        @classmethod
        @public
        def fn_c(cls, **a):
            return a['a']-a['b']-cls.c

    test=Test()
    dispatch.register_instance(test)
    mock_request = Mock(RPCRequest)
    mock_request.args = args
    mock_request.kwargs = kwargs
    mock_request.method = method
    dispatch._dispatch(mock_request, getattr(protocol, '_caller', None))
    if inspect.isclass(result) and issubclass(result, Exception):
        assert type(mock_request.error_respond.call_args[0][0]) == result
    else:
        mock_request.respond.assert_called_with(result)


def test_async_class_method_argument_error(async_dispatch, invoke_with, event_loop):
    method, args, kwargs, result = invoke_with

    protocol = JSONRPCProtocol()

    class Test:
        c = 0
        @classmethod
        @public
        async def fn_a(cls, a, b):
            return a-b-cls.c

        @classmethod
        @public
        async def fn_b(cls, *a):
            return a[0]-a[1]-cls.c

        @classmethod
        @public
        async def fn_c(cls, **a):
            return a['a']-a['b']-cls.c

    test=Test()
    async_dispatch.register_instance(test)
    mock_request = Mock(RPCRequest)
    mock_request.args = args
    mock_request.kwargs = kwargs
    mock_request.method = method
    event_loop.run_until_complete(async_dispatch._dispatch(mock_request))
    if inspect.isclass(result) and issubclass(result, Exception):
        assert type(mock_request.error_respond.call_args[0][0]) == result
    else:
        mock_request.respond.assert_called_with(result)


def test_class_method_validation(dispatch):
    class Test:
        @classmethod
        def f(cls, a, b):
            return a+b
    inst = Test()

    dispatch.validate_parameters(inst.f, [1, 2], {})
    with pytest.raises(InvalidParamsError):
        dispatch.validate_parameters(inst.f, [1], {})


def test_async_class_method_validation(async_dispatch):
    class Test:
        @classmethod
        async def f(cls, a, b):
            return a+b
    inst = Test()

    async_dispatch.validate_parameters(inst.f, [1, 2], {})
    with pytest.raises(InvalidParamsError):
        async_dispatch.validate_parameters(inst.f, [1], {})
