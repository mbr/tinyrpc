#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import RPCProtocol, RPCRequest, RPCReply, InvalidRequestError,\
               MethodNotFoundError, ServerError

import json


class JSONRPCParseError(InvalidRequestError):
    jsonrpc_error_code = -32700
    message = 'Parse error'


class JSONRPCInvalidRequestError(InvalidRequestError):
    jsonrpc_error_code = -32600
    message = 'Invalid Request'


class JSONRPCMethodNotFoundError(MethodNotFoundError):
    jsonrpc_error_code = -32601
    message = 'Method not found'


class JSONRPCInvalidParamsError(InvalidRequestError):
    jsonrpc_error_code = -32602
    message = 'Invalid params'


class JSONRPCInternalError(InvalidRequestError):
    jsonrpc_error_code = -32603
    message = 'Internal error'


class JSONRPCReply(RPCReply):
    def serialize(self):
        resp = {
            'jsonrpc': JSON_RPC_VERSION,
            'id': return_value.context
        }

        if not self.error:
            resp['result'] = self.rv
        else:
            resp['error'] = str(self.error)

        return json.dumps(resp)


class JSONRPCRequest(RPCRequest):
    pass


class JSONRPCProtocol(RPCProtocol):
    """JSONRPC protocol implementation.

    Currently, only version 2.0 is supported."""

    JSON_RPC_VERSION = "2.0"
    _ALLOWED_REQUEST_KEYS = sorted(['id', 'jsonrpc', 'method', 'params'])

    def parse_request(self, data):
        try:
            req = json.loads(data)
        except Exception as e:
            raise JSONRPCParseError

        for k in req.iterkeys():
            if not k in self._ALLOWED_REQUEST_KEYS:
                raise JSONRPCInvalidRequestError

        if req['jsonrpc'] != self.JSON_RPC_VERSION:
            raise JSONRPCInvalidRequestError

        if not isinstance(req['method'], basestring):
            raise JSONRPCMethodNotFoundError

        request = JSONRPCRequest()
        request.method = str(req['method'])
        request._jsonrpc_id = req['id']

        if isinstance(req['params'], list):
            request.args = req['params']
        elif isinstance(req['params'], dict):
            request.kwargs = req['params']
        else:
            raise JSONRPCInvalidParamsError

        return request
