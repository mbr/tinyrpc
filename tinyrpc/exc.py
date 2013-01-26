#!/usr/bin/env python
# -*- coding: utf-8 -*-

class RPCError(Exception):
    """Base class for all excetions thrown by :py:mod:`tinyrpc`."""


class BadRequestError(RPCError):
    """Base class for all exceptions that caused the processing of a request to
    abort."""

    def error_respond(self):
        """Create :py:class:`~tinyrpc.RPCErrorResponse` for handling error.

        :return: A error responce instance or ``None``, if the protocol decides
                 to drop the error silently."""
        raise RuntimeError('Not implemented')


class InvalidRequestError(BadRequestError):
    """A request made was malformed and could not be parsed."""


class InvalidReplyError(RPCError):
    pass


class MethodNotFoundError(RPCError):
    pass


class ServerError(RPCError):
    pass
