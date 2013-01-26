#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from tinyrpc.dispatch import RPCDispatcher, public


@pytest.fixture
def dispatch():
    return RPCDispatcher()


@pytest.fixture()
def subdispatch():
    return RPCDispatcher()


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
