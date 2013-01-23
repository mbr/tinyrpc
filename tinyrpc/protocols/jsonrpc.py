#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import RPCProtocol

import json


class JSONRPCProtocol(RPCProtocol):
    """JSONRPC protocol implementation.

    Currently, only version 2.0 is supported."""

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
