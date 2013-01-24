#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import RPCProtocol, RPCRequest, RPCErrorResponse, InvalidRequestError,\
               MethodNotFoundError, ServerError, InvalidReplyError,\
               RPCSuccessResponse, RPCError

import json

class FixedErrorMessageMixin(object):
    def __init__(self, *args, **kwargs):
        if not args:
            args = [self.message]
        super(FixedErrorMessageMixin, self).__init__(*args, **kwargs)


class JSONRPCParseError(FixedErrorMessageMixin, InvalidRequestError):
    jsonrpc_error_code = -32700
    message = 'Parse error'


class JSONRPCInvalidRequestError(FixedErrorMessageMixin, InvalidRequestError):
    jsonrpc_error_code = -32600
    message = 'Invalid Request'


class JSONRPCMethodNotFoundError(FixedErrorMessageMixin, MethodNotFoundError):
    jsonrpc_error_code = -32601
    message = 'Method not found'


class JSONRPCInvalidParamsError(FixedErrorMessageMixin, InvalidRequestError):
    jsonrpc_error_code = -32602
    message = 'Invalid params'


class JSONRPCInternalError(FixedErrorMessageMixin, InvalidRequestError):
    jsonrpc_error_code = -32603
    message = 'Internal error'


class JSONRPCSuccessResponse(RPCSuccessResponse):
    def serialize(self):
        return json.dumps({
            'jsonrpc': JSONRPCProtocol.JSON_RPC_VERSION,
            'id': self._jsonrpc_id,
            'result': self.rv,
        })


class JSONRPCErrorResponse(RPCErrorResponse):
    def serialize(self):
        return json.dumps({
            'jsonrpc': JSONRPCProtocol.JSON_RPC_VERSION,
            'id': self._jsonrpc_id,
            'error': {
                'message': str(self.error),
                'code': self._jsonrpc_error_code,
            }
        })


class JSONRPCRequest(RPCRequest):
    def error_respond(self, error):
        if not self._jsonrpc_id:
            return None

        assert isinstance(error, (Exception, basestring))
        response = JSONRPCErrorResponse()

        if isinstance(error, Exception):
            if hasattr(error, 'jsonrpc_error_code'):
                code = error.jsonrpc_error_code
                msg = str(error)
            elif isinstance(error, InvalidRequestError):
                code = JSONRPCInvalidRequestError.jsonrpc_error_code
                msg = JSONRPCInvalidRequestError.message
            elif isinstance(error, MethodNotFoundError):
                code = JSONRPCMethodNotFoundError.jsonrpc_error_code
                msg = JSONRPCMethodNotFoundError.message
            else:
                code = JSONRPCInternalError.jsonrpc_error_code
                msg = JSONRPCInternalError.message
        else:
            code = -32000
            msg = error

        response.error = msg
        response._jsonrpc_id = self._jsonrpc_id
        response._jsonrpc_error_code = code
        return response

    def respond(self, rv):
        response = JSONRPCSuccessResponse()

        if not self._jsonrpc_id:
            return None

        response.rv = rv

        return response


class JSONRPCProtocol(RPCProtocol):
    """JSONRPC protocol implementation.

    Currently, only version 2.0 is supported."""

    JSON_RPC_VERSION = "2.0"
    _ALLOWED_REPLY_KEYS = sorted(['id', 'jsonrpc', 'error', 'result'])
    _ALLOWED_REQUEST_KEYS = sorted(['id', 'jsonrpc', 'method', 'params'])

    def parse_reply(self, data):
        try:
            rep = json.loads(data)
        except Exception as e:
            raise InvalidReplyError(e)

        for k in rep.iterkeys():
            if not k in self._ALLOWED_REPLY_KEYS:
                raise InvalidReplyError('Key not allowed: %s' % k)

        if rep['jsonrpc'] != self.JSON_RPC_VERSION:
            raise InvalidReplyError('Wrong JSONRPC version')

        if not 'id' in rep:
            raise InvalidReplyError('Missing id in response')

        if ('error' in rep) == ('result' in rep):
            raise InvalidReplyError(
                'Reply must contain exactly one of result and error.'
            )

        if 'error' in rep:
            response = JSONRPCErrorResponse()
            error = rep['error']
            response.error = error['message']
            response._jsonrpc_error_code = error['code']
        else:
            response = JSONRPCSuccessResponse()
            response.rv = rep.get('result', None)

        response._jsonrpc_id = rep['id']

        return response

    def parse_request(self, data):
        try:
            req = json.loads(data)
        except Exception as e:
            raise JSONRPCParseError()

        if isinstance(req, list):
            # batch request
            requests = []
            for subreq in req:
                try:
                    requests.append(self._parse_subrequest(subreq))
                except RPCError as e:
                    requests.append(e)
                except Exception as e:
                    requests.append(JSONRPCInvalidRequestError())

            if not requests:
                raise JSONRPCInvalidRequestError()
            return requests
        else:
            return self._parse_subrequest(req)

    def _parse_subrequest(self, req):
        for k in req.iterkeys():
            if not k in self._ALLOWED_REQUEST_KEYS:
                raise JSONRPCInvalidRequestError()

        if req['jsonrpc'] != self.JSON_RPC_VERSION:
            raise JSONRPCInvalidRequestError()

        if not isinstance(req['method'], basestring):
            raise JSONRPCMethodNotFoundError()

        request = JSONRPCRequest()
        request.method = str(req['method'])
        request._jsonrpc_id = req.get('id', None)

        params = req.get('params', None)
        if params != None:
            if isinstance(params, list):
                request.args = req['params']
            elif isinstance(params, dict):
                request.kwargs = req['params']
            else:
                raise JSONRPCInvalidParamsError()

        return request
