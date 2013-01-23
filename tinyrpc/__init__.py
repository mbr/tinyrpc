#!/usr/bin/env python
# -*- coding: utf-8 -*-

class RPCProtocol(object):
    """Base class for all protocol implementations."""

    def parse_request(data):
        """Parses a request given as a string and returns it as a
        :py:class:`CallSpec` structure."""
        pass

    def parse_rv(data):
        """Given a return value encoded in a string, restore the return
        value."""

    def serialize_request(callspec):
        """Transforms a :py:class:`CallSpec` into a string to be passed on to
        a transport."""
        pass

    def serialize_rv(rv):
        """Serializes a return value into a message string, ready to be sent
        back."""
        pass


class RPCDispatcher(object):
    def get_method(method_name, args=None, kwargs=None):
        pass


from collections import namedtuple


def run_server(transport, protocol, dispatcher):
    data_in, transport_ctx = transport.get_request()
    function_call, protocol_ctx = protocol.parse_request(data_in)
    return_value = dispatcher.call(function_call)
    data_out = protocol.serialize_response(return_value, protocol_ctx)
    transport.send_reply(data_out, transport_ctx)


class RPCError(Exception):
    pass


class InvalidRequestError(RPCError):
    pass


class MethodNotFoundError(RPCError):
    pass


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


CallSpec = namedtuple('CallSpec', ['method', 'args', 'kwargs'])
ReturnValue = namedtuple('ReturnValue', ['value', 'error'])
