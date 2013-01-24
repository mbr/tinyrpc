#!/usr/bin/env python
# -*- coding: utf-8 -*-

class RPCRequest(object):
    method = None
    """The name of the method to be called."""
    args = None
    """The positional arguments of the method call."""
    kwargs = None
    """The keyword arguments of the method call."""

    def error_respond(self, error):
        """Creates an error response.

        Create a response indicating that an error has occured.

        :param: An exception or a string describing the error.

        :return: A response or ``None`` to indicate that no error should be sent
        out.
        """
        raise RuntimeError('Not implemented')

    def respond(self, rv):
        """Create a response.

        This creates and returns an instance of a protocol-specific subclass of
        :py:class:`~tinyrpc.RPCResponse`.

        :param rv: Passed on to new response instance.

        :return: A response or ``None`` to indicate this request does not expect a
        response.
        """
        raise RuntimeError('Not implemented')

    def serialize(self):
        """Returns a serialization of the request.

        :return: A string to be passed on to a transport.
        """
        raise RuntimeError('Not implemented')


class RPCResponse(object):
    """RPC call response base class."""

    is_error = False
    """If true, the rpc call failed."""

    def serialize(self):
        """Returns a serialization of the response.

        :return: A reply to be passed on to a transport.
        """
        raise RuntimeError('Not implemented')


class RPCErrorResponse(RPCResponse):
    is_error = True

    error = None
    """The error that has occured, an exception or a string."""


class RPCSuccessResponse(RPCResponse):
    is_error = False

    rv = None
    """The rpc call's return value."""


class RPCProtocol(object):
    """Base class for all protocol implementations."""

    def create_request(self, method, args, kwargs):
        """Creates a new RPCRequest object.

        :param method: The method name to invoke.
        :param args: The positional arguments to call the method with.
        :param kwargs: The keyword arguments to call the method with.
        :return: A new :py:class:`~tinyrpc.RPCRequest` instance.
        """
        raise RuntimeError('Not implemented')

    def create_error_response(self, error):
        """Creates an error response independent of a request.

        Usually, if an error occurs,
        :py:func:`~tinyrpc.RPCResponse.error_respond` should be called.
        If errors occur before an instance of :py:class:`~tinyrpc.RPCResponse`
        can be instantiated, use this function to generate a reply
        :param error: Exception or string.
        :return: A `~tinyrpc.RPCErrorResponse` instance.
        """
        raise RuntimeError('Not implemented')

    def parse_request(self, data):
        """Parses a request given as a string and returns an
        :py:class:`RPCRequest` instance.

        :return: An instanced request.
        """
        raise RuntimeError('Not implemented')

    def parse_reply(self, data):
        """Parses a reply and returns an :py:class:`RPCResponse` instance.

        :return: An instanced response.
        """
        raise RuntimeError('Not implemented')


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


class RPCError(Exception):
    pass


class InvalidRequestError(RPCError):
    pass


class InvalidReplyError(RPCError):
    pass


class MethodNotFoundError(RPCError):
    pass


class ServerError(RPCError):
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
