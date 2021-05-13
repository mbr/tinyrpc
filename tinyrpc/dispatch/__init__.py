#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dispatcher
==========

Given an RPC request the dispatcher will try to locate a server function that
implements the request and will call that function returning its return value
to the caller.
"""

import inspect

from .. import exc


def public(name=None):
    """Decorator. Mark a method as eligible for registration by a dispatcher.

    The dispatchers :py:func:`~tinyrpc.dispatch.RPCDispatcher.register_instance` function
    will do the actual registration of the marked method.

    The difference with :py:func:`~tinyrpc.dispatch.RPCDispatcher.public` is that this decorator does
    not register with a dispatcher, therefore binding the marked methods with a dispatcher is delayed
    until runtime.
    It also becomes possible to bind with multiple dispatchers.

    :param name: The name to register the function with.
    :type name: str or None

    Example:

    .. code-block:: python

        def class Baz(object):
            def not_exposed(self);
                # ...

            @public('do_something')
            def visible_method(arg1):
                # ...

        baz = Baz()
        dispatch = RPCDispatcher()
        dispatch.register_instance(baz, 'bazzies`)
        # Baz.visible_method is now callable via RPC as bazzies.do_something

    ``@public`` is a shortcut for ``@public()``.
    """
    if callable(name):
        f = name
        f._rpc_public_name = f.__name__
        return f

    def _(f):
        f._rpc_public_name = name or f.__name__
        return f

    return _


class RPCDispatcher(object):
    """Stores name-to-method mappings."""

    def __init__(self):
        self.method_map = {}
        self.subdispatchers = {}

    def public(self, name=None):
        """Convenient decorator.

        Allows easy registering of functions to this dispatcher. Example:

        .. code-block:: python

            dispatch = RPCDispatcher()

            @dispatch.public
            def foo(bar):
                # ...

            class Baz(object):
                def not_exposed(self):
                    # ...

                @dispatch.public(name='do_something')
                def visible_method(arg1)
                    # ...

        :param str name: Name to register callable with.
        """
        if callable(name):
            self.add_method(name)
            return name

        def _(f):
            self.add_method(f, name=name)
            return f

        return _

    def add_subdispatch(self, dispatcher, prefix=''):
        """Adds a subdispatcher, possibly in its own namespace.

        :param dispatcher: The dispatcher to add as a subdispatcher.
        :type dispatcher: RPCDispatcher
        :param str prefix: A prefix. All of the new subdispatchers methods will be
                       available as prefix + their original name.
        """
        self.subdispatchers.setdefault(prefix, []).append(dispatcher)

    def add_method(self, f, name=None):
        """Add a method to the dispatcher.

        :param f: Callable to be added.
        :type f: callable
        :param str name: Name to register it with. If ``None``, ``f.__name__`` will
                     be used.
        :raises ~tinyrpc.exc.RPCError: When the `name` is already registered.
        """
        assert callable(f), "method argument must be callable"
        # catches a few programming errors that are
        # commonly silently swallowed otherwise
        if not name:
            name = f.__name__

        if name in self.method_map:
            raise exc.RPCError('Name %s already registered')

        self.method_map[name] = f

    def get_method(self, name):
        """Retrieve a previously registered method.

        Checks if a method matching ``name`` has been registered.

        If :py:func:`get_method` cannot find a method, every subdispatcher
        with a prefix matching the method name is checked as well.

        :param str name: Function to find.
        :returns: The callable implementing the function.
        :rtype: callable
        :raises: :py:exc:`~tinyrpc.exc.MethodNotFoundError`
        """
        if name in self.method_map:
            return self.method_map[name]

        for prefix, subdispatchers in self.subdispatchers.items():
            if name.startswith(prefix):
                for sd in subdispatchers:
                    try:
                        return sd.get_method(name[len(prefix):])
                    except exc.MethodNotFoundError:
                        pass

        raise exc.MethodNotFoundError(name)

    def register_instance(self, obj, prefix=''):
        """Create new subdispatcher and register all public object methods on
        it.

        To be used in conjunction with the :py:func:`public`
        decorator (*not* :py:func:`RPCDispatcher.public`).

        :param obj: The object whose public methods should be made available.
        :type obj: object
        :param str prefix: A prefix for the new subdispatcher.
        """
        dispatch = self.__class__()
        for name, f in inspect.getmembers(
                obj, lambda f: callable(f) and hasattr(f, '_rpc_public_name')):
            dispatch.add_method(f, f._rpc_public_name)

        # add to dispatchers
        self.add_subdispatch(dispatch, prefix)

    def dispatch(self, request):
        """Fully handle request.

        The dispatch method determines which method to call, calls it and
        returns a response containing a result.

        No exceptions will be thrown, rather, every exception will be turned
        into a response using :py:func:`~tinyrpc.RPCRequest.error_respond`.

        If a method isn't found, a :py:exc:`~tinyrpc.exc.MethodNotFoundError`
        response will be returned. If any error occurs outside of the requested
        method, a :py:exc:`~tinyrpc.exc.ServerError` without any error
        information will be returend.

        If the method is found and called but throws an exception, the
        exception thrown is used as a response instead. This is the only case
        in which information from the exception is possibly propagated back to
        the client, as the exception is part of the requested method.

        :py:class:`~tinyrpc.RPCBatchRequest` instances are handled by handling
        all its children in order and collecting the results, then returning an
        :py:class:`~tinyrpc.RPCBatchResponse` with the results.

        :param request: The request containing the function to be called and its parameters.
        :type request: ~tinyrpc.protocols.RPCRequest
        :return: The result produced by calling the requested function.
        :rtype: ~tinyrpc.protocols.RPCResponse
        :raises ~exc.MethodNotFoundError: If the requested function is not published.
        :raises ~exc.ServerError: If some other error occurred.

        .. Note::

            The :py:exc:`~tinyrpc.exc.ServerError` is raised for any kind of exception not
            raised by the called function itself or :py:exc:`~tinyrpc.exc.MethodNotFoundError`.
        """
        if hasattr(request, 'create_batch_response'):
            results = [self._dispatch(req) for req in request]

            response = request.create_batch_response()
            if response is not None:
                response.extend(results)

            return response
        else:
            return self._dispatch(request)

    def _dispatch(self, request):
        try:
            method = self.get_method(request.method)
        except exc.MethodNotFoundError as e:
            return request.error_respond(e)
        except Exception:
            # unexpected error, do not let client know what happened
            return request.error_respond(exc.ServerError())

        # we found the method
        try:
            if self.validator is not None:
                self.validator(method, request.args, request.kwargs)
            result = method(*request.args, **request.kwargs)
        except Exception as e:
            # an error occurred within the method, return it
            return request.error_respond(e)

        # respond with result
        return request.respond(result)

    def validate_parameters(self, method, args, kwargs):
        """Verify that `*args` and `**kwargs` are appropriate parameters for `method`.

        :param method: A callable.
        :param args: List of positional arguments for `method`
        :param kwargs: Keyword arguments for `method`
        :raises ~tinyrpc.exc.InvalidParamsError:
            Raised when the provided arguments are not acceptable for `method`.
        """
        if hasattr(method, '__code__'):
            try:
                inspect.getcallargs(method, *args, **kwargs)
            except TypeError:
                raise exc.InvalidParamsError()

    validator = validate_parameters
    """Dispatched function parameter validatation.

    :type: callable
    
    By default this attribute is set to :py:func:`validate_parameters`.
    The value can be set to any callable implementing the same interface
    as :py:func:`validate_parameters` or to `None` to disable validation
    entirely.
    """

