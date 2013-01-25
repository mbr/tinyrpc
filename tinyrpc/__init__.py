#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .protocols import *
from .exc import *

#class RPCDispatcher(object):
#    def get_method(method_name, args=None, kwargs=None):
#        pass
#
#
#
#
#def run_server(transport, protocol, dispatcher):
#    data_in, transport_ctx = transport.get_request()
#    function_call, protocol_ctx = protocol.parse_request(data_in)
#    return_value = dispatcher.call(function_call)
#    data_out = protocol.serialize_response(return_value, protocol_ctx)
#    transport.send_reply(data_out, transport_ctx)

# IDEA: nest dispatchers, allowing trees - decouples classes from
#       instance dispatchers?
class Dispatcher(object):
    def __init__(self, methods=None):
        self.methods = methods or {}

    def call(spec):
        if not spec.method in self.methods:
            return ReturnValue(None, MethodNotFoundError(spec.method))

        try:
            val = self.methods[spec.method](*spec.args, **spec.kwargs)
            return ReturnValue(val, None)
        except Exception as e:
            return ReturnValue(None, e)

    def expose(f):
        self.methods[f.__name__] = f
        return f

    def register_method(self, name, method):
        self.methods[name] = method
