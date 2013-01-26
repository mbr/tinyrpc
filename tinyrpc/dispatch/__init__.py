#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect

from ..exc import *


def public(name=None):
    """Set RPC name on function.

    This function decorator will set the ``_rpc_public_name`` attribute on a
    function, causing it to be picked up if an instance of its parent class is
    registered using
    :py:func:`~tinyrpc.dispatch.RPCDispatcher.register_instance`.

    ``@public`` is a shortcut for ``@public()``.

    :param name: The name to register the function with.
    """
    # called directly with function
    if callable(name):
        f = name
        f._rpc_public_name = f.__name__
        return f

    def _(f):
        f._rpc_public_name = name or f.__name__
        return f

    return _


class RPCDispatcher(object):
    """Stores name-to-method mappings."""

    def __init__(self):
        self.method_map = {}
        self.subdispatchers = {}

    def add_subdispatch(self, dispatcher, prefix=''):
        """Adds a subdispatcher, possibly in its own namespace.

        :param dispatcher: The dispatcher to add as a subdispatcher.
        :param prefix: A prefix. All of the new subdispatchers methods will be
                       available as prefix + their original name.
        """
        self.subdispatchers.setdefault(prefix, []).append(dispatcher)

    def add_method(self, f, name=None):
        """Add a method to the dispatcher.

        :param f: Callable to be added.
        :param name: Name to register it with. If ``None``, ``f.__name__`` will
                     be used.
        """
        if not name:
            name = f.__name__

        if name in self.method_map:
            raise RPCError('Name %s already registered')

        self.method_map[name] = f

    def get_method(self, name):
        """Retrieve a previously registered method.

        Checks if a method matching ``name`` has been registered.

        If :py:func:`get_method` cannot find a method, every subdispatcher
        with a prefix matching the method name is checked as well.

        If a method isn't found, a :py:class:`KeyError` is thrown.

        :param name: Callable to find.
        :param return: The callable.
        """
        if name in self.method_map:
            return self.method_map[name]

        for prefix, subdispatchers in self.subdispatchers.iteritems():
            if name.startswith(prefix):
                for sd in subdispatchers:
                    try:
                        return sd.get_method(name[len(prefix):])
                    except KeyError:
                        pass

        raise KeyError(name)

    def public(self, name=None):
        """Convenient decorator.

        Allows easy registering of functions to this dispatcher. Example:

        .. code-block:: python

            dispatch = RPCDispatcher()

            @dispatch.public
            def foo(bar):
                # ...

            class Baz(object):
                def not_exposed(self):
                    # ...

                @dispatch.public(name='do_something')
                def visible_method(arg1)
                    # ...

        :param name: Name to register callable with
        """
        if callable(name):
            self.add_method(name)
            return name

        def _(f):
            self.add_method(f, name=name)
            return f

        return _

    def register_instance(self, obj, prefix=''):
        """Create new subdispatcher and register all public object methods on
        it.

        To be used in conjunction with the :py:func:`tinyrpc.dispatch.public`
        decorator (*not* :py:func:`tinyrpc.dispatch.RPCDispatcher.public`).

        :param obj: The object whose public methods should be made available.
        :param prefix: A prefix for the new subdispatcher.
        """
        dispatch = self.__class__()
        for name, f in inspect.getmembers(
            obj, lambda f: callable(f) and hasattr(f, '_rpc_public_name')
        ):
            dispatch.add_method(f, f._rpc_public_name)

        # add to dispatchers
        self.add_subdispatch(dispatch, prefix)
