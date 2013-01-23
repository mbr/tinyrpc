#!/usr/bin/env python
# -*- coding: utf-8 -*-

class RPCProtocol(object):
    def handle_request(request):
        # do decoding
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


import json


class JSONRPCProtocol(RPCProtocol):
    JSON_RPC_VERSION = "2.0"
    _ALLOWED_REQUEST_KEYS = sorted(['id', 'jsonrpc', 'method', 'params'])

    def parse_request(data):
        req = json.loads(data)

        for k in req.iterkeys():
            if not k in _ALLOWED_REQUEST_KEYS:
                raise InvalidRequestError(
                    '%s not a valid request key.' % k
                )

        if req['jsonrpc'] != JSON_RPC_VERSION:
            raise InvalidRequestError(
                'Only supports jsonrpc %s' % JSON_RPC_VERSION
            )

        if not isinstance(req['method'], basestring):
            raise InvalidRequestError(
                'method name must be a string: %s' % req['method']
            )

        if isinstance(req['params'], list):
            return CallSpec(
                str(req['method']),
                req['params'],
                None,
            ), req['id']

        if isinstance(req['params'], dict):
            return CallSpec(
                str(req['method']),
                None,
                req['params'],
            ), req['id']

        raise InvalidRequestError(
            'params must be either array or object.'
        )

    def serialize_response(return_value):
        resp = {
            'jsonrpc': JSON_RPC_VERSION,
            'id': return_value.context
        }

        if return_value.status == 'ok':
            resp['result'] = return_value.value
        elif return_value.status == 'error':
            resp['error'] = return_value.value
        else:
            resp['error'] = str(return_value.value)

        return json.dumps(resp)
