#!/usr/bin/env python
# -*- coding: utf-8 -*-

class RPCRequest(object):
    method = None
    """The name of the method to be called."""
    args = None
    """The positional arguments of the method call."""
    kwargs = None
    """The keyword arguments of the method call."""

    def reply(self, error, rv):
        """Create a reply.

        This creates and returns an instance of a protocol-specific subclass of
        :py:class:`~tinyrpc.RPCReply`.

        :param error: Passed on to new reply instance.
        :param rv: Passed on to new reply instance.

        :return: A reply or ``None`` to indicate this request does not expect a
        reply.
        """
        raise RuntimeError('Not implemented')

    def serialize(self):
        """Returns a serialization of the request.

        :return: A string to be passed on to a transport.
        """
        raise RuntimeError('Not implemented')


class RPCReply(object):
    error = None
    """If not ``None``, an error has occured (i.e. an exception has been
    thrown) and this attribute contains the exception."""

    rv = None
    """The function calls return value."""

    def serialize(self):
        """Returns a serialization of the reply.

        :return: A string to be passed on to a transport.
        """
        raise RuntimeError('Not implemented')


class RPCProtocol(object):
    """Base class for all protocol implementations."""

    def create_error_message(self, error):
        """Transforms an exception that occured outside of the desired function
        into a possible reply-message.

        :error: An exception.
        :return: ``None``, if no action should be taken, or a string containing
        the reply to send back.
        """
        raise RuntimeError('Not implemented')

    def create_request(self, method, args, kwargs):
        raise RuntimeError('Not implemented')

    def parse_request(self, data):
        """Parses a request given as a string and returns an
        :py:class:`RPCRequest` instance.

        :return: An instanced request.
        """
        raise RuntimeError('Not implemented')

    def parse_reply(data):
        """Parses a reply and returns an :py:class:`RPCReply` instance.

        :return: An instanced reply.
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
