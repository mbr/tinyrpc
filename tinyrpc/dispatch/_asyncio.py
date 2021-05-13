"""
This module implements an asyncio-based async dispatcher
"""
from tinyrpc.dispatch import RPCDispatcher, public
from tinyrpc import exc


class AsyncioRPCDispatcher(RPCDispatcher):
    """Stores name-to-method mappings. Support async methods."""

    async def dispatch(self, request):
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
            # TODO: replace async comprehension with async loop to support older pythons?
            results = [await self._dispatch(req) for req in request]

            response = request.create_batch_response()
            if response is not None:
                response.extend(results)

            return response
        else:
            return await self._dispatch(request)

    async def _dispatch(self, request):
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
            # TODO: catch error caused by non-awaitable return value
            result = await method(*request.args, **request.kwargs)
        except Exception as e:
            # an error occurred within the method, return it
            return request.error_respond(e)

        # respond with result
        return request.respond(result)
