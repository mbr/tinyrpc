#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import RPCBatchProtocol, RPCRequest, RPCResponse, RPCErrorResponse,\
               InvalidRequestError, MethodNotFoundError, ServerError,\
               InvalidReplyError, RPCError, RPCBatchRequest, RPCBatchResponse

import msgpack
import six


class FixedErrorMessageMixin(object):
    def __init__(self, *args, **kwargs):
        if not args:
            args = [self.message]
        super(FixedErrorMessageMixin, self).__init__(*args, **kwargs)

    def error_respond(self):
        response = MSGPACKRPCErrorResponse()

        response.error = self.message
        response.unique_id = None
        response._msgpackrpc_error_code = self.msgpackrpc_error_code
        return response



class MSGPACKRPCParseError(FixedErrorMessageMixin, InvalidRequestError):
    msgpackrpc_error_code = -32700
    message = 'Parse error'


class MSGPACKRPCInvalidRequestError(FixedErrorMessageMixin, InvalidRequestError):
    msgpackrpc_error_code = -32600
    message = 'Invalid Request'


class MSGPACKRPCMethodNotFoundError(FixedErrorMessageMixin, MethodNotFoundError):
    msgpackrpc_error_code = -32601
    message = 'Method not found'


class MSGPACKRPCInvalidParamsError(FixedErrorMessageMixin, InvalidRequestError):
    msgpackrpc_error_code = -32602
    message = 'Invalid params'


class MSGPACKRPCInternalError(FixedErrorMessageMixin, InvalidRequestError):
    msgpackrpc_error_code = -32603
    message = 'Internal error'


class MSGPACKRPCServerError(FixedErrorMessageMixin, InvalidRequestError):
    msgpackrpc_error_code = -32000
    message = ''


class MSGPACKRPCSuccessResponse(RPCResponse):
    def _to_dict(self):
        return [
            1,
            self.unique_id,
            None,
            self.result,
        ]

    def serialize(self):
        return msgpack.dumps(self._to_dict())


class MSGPACKRPCErrorResponse(RPCErrorResponse):
    def _to_dict(self):
        return [
            1,
            self.unique_id,
            "Error %d: %s" % (self._msgpackrpc_error_code, str(self.error)),
            None,
        ]

    def serialize(self):
        return msgpack.dumps(self._to_dict())


def _get_code_and_message(error):
    assert isinstance(error, (Exception, six.string_types))
    if isinstance(error, Exception):
        if hasattr(error, 'msgpackrpc_error_code'):
            code = error.msgpackrpc_error_code
            msg = str(error)
        elif isinstance(error, InvalidRequestError):
            code = MSGPACKRPCInvalidRequestError.msgpackrpc_error_code
            msg = MSGPACKRPCInvalidRequestError.message
        elif isinstance(error, MethodNotFoundError):
            code = MSGPACKRPCMethodNotFoundError.msgpackrpc_error_code
            msg = MSGPACKRPCMethodNotFoundError.message
        else:
            # allow exception message to propagate
            code = MSGPACKRPCServerError.msgpackrpc_error_code
            msg = str(error)
    else:
        code = -32000
        msg = error

    return code, msg


class MSGPACKRPCRequest(RPCRequest):
    def error_respond(self, error):
        if not self.unique_id:
            return None

        response = MSGPACKRPCErrorResponse()

        code, msg = _get_code_and_message(error)

        response.error = msg
        response.unique_id = self.unique_id
        response._msgpackrpc_error_code = code
        return response

    def respond(self, result):
        response = MSGPACKRPCSuccessResponse()

        if not self.unique_id:
            return None

        response.result = result
        response.unique_id = self.unique_id
        return response

    def _to_dict(self):
        jdata = [
            0, 
            self.unique_id,
            self.method, 
            self.args if self.args is not None else []
        ]
        return jdata

    def serialize(self):
        return msgpack.dumps(self._to_dict())


class MSGPACKRPCBatchRequest(RPCBatchRequest):
    def __init__(self): 
        raise NotImplementedError


class MSGPACKRPCBatchResponse(RPCBatchResponse):
    def __init__(self): 
        raise NotImplementedError

class MSGPACKRPCProtocol(RPCBatchProtocol):
    """MSGPACKRPC protocol implementation."""

    def __init__(self, *args, **kwargs):
        super(MSGPACKRPCProtocol, self).__init__(*args, **kwargs)
        self._id_counter = 0

    def _get_unique_id(self):
        self._id_counter += 1
        return self._id_counter

    def create_batch_request(self, requests=None):
        raise NotImplementedError

    def create_request(self, method, args=None, kwargs=None, one_way=False):
        if kwargs:
            raise InvalidRequestError('Does not support kwargs')

        request = MSGPACKRPCRequest()

        if not one_way:
            request.unique_id = self._get_unique_id()

        request.method = method
        request.args = args
        request.kwargs = None

        return request

    def parse_reply(self, data):
        if six.PY3 and isinstance(data, bytes):
            # zmq won't accept unicode strings, and this is the other
            # end; decoding non-unicode strings back into unicode
            data = data.decode()

        try:
            rep = msgpack.loads(data)
        except Exception as e:
            raise InvalidReplyError(e)
        
        if not len(rep) == 4:
            raise InvalidReplyError('MSGPACKRPC spec requires reply of length 4')

        if rep[2] is not None and rep[2] is not None:
            raise InvalidReplyError(
                'Reply must contain only one of result and error.'
            )

        if rep[2] is not None:
            response = MSGPACKRPCErrorResponse()
            error = rep[2]
            response.error = str(error)
            #response._msgpackrpc_error_code = error['code']
        else:
            response = MSGPACKRPCSuccessResponse()
            response.result = rep[3]

        response.unique_id = rep[1]

        return response

    def parse_request(self, data):
        if six.PY3 and isinstance(data, bytes):
            # zmq won't accept unicode strings, and this is the other
            # end; decoding non-unicode strings back into unicode
            data = data.decode()

        try:
            req = msgpack.loads(data)
        except Exception as e:
            raise MSGPACKRPCParseError()

        if isinstance(req, list) and len(req) == 4:
            return self._parse_subrequest(req)
        else:
            raise MSGPACKRPCInvalidRequestError()

    def _parse_subrequest(self, req):
        
        if not isinstance(req[2], six.string_types):
            raise MSGPACKRPCInvalidRequestError()

        request = MSGPACKRPCRequest()
        request.method = req[2]
        request.unique_id = req[1]

        params = req[3]
        if params != None:
            if isinstance(params, list):
                request.args = params
            else:
                raise MSGPACKRPCInvalidParamsError()

        return request
