#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect

from ..exc import *


def public(name=None):
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
    def __init__(self):
        self.method_map = {}
        self.subdispatchers = {}

    def add_subdispatch(self, dispatcher, prefix=''):
        self.subdispatchers.setdefault(prefix, []).append(dispatcher)

    def add_method(self, f, name=None):
        if not name:
            name = f.__name__

        if name in self.method_map:
            raise RPCError('Name %s already registered')

        self.method_map[name] = f

    def get_method(self, name):
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
        if callable(name):
            self.add_method(name)
            return name

        def _(f):
            self.add_method(f, name=name)
            return f

        return _

    def register_instance(self, obj, prefix=''):
        # create new dispatcher and register all public object methods on it
        dispatch = self.__class__()
        for name, f in inspect.getmembers(
            obj, lambda f: callable(f) and hasattr(f, '_rpc_public_name')
        ):
            dispatch.add_method(f, f._rpc_public_name)

        # add to dispatchers
        self.add_subdispatch(dispatch, prefix)
