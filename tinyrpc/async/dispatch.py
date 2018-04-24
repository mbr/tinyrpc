import asyncio

from tinyrpc.dispatch import RPCDispatcher


class AsyncRPCDispatcher(RPCDispatcher):
    """
    Override default RPCDispatcher to implement async-await calls
    Code is identical to server.RPCDispatcher, only async-await added
    """

    async def dispatch(self, request, caller=None):
        if hasattr(request, 'create_batch_response'):
            results = await asyncio.gather(*(self._dispatch(req, caller)
                                             for req in request))

            response = request.create_batch_response()
            if response is not None:
                response.extend(results)

            return response
        else:
            return await self._dispatch(request, caller)

    async def _dispatch(self, request, caller):
        """
        Pass additional arguments "id" and "context" to handlers
        """
        assert asyncio.iscoroutine(caller) or \
               asyncio.iscoroutinefunction(caller), 'caller must be awaitable'

        try:
            method = self.get_method(request.method)
            if caller is not None:
                result = await caller(method, request.args, request.kwargs)
            else:
                result = await method(*request.args, **request.kwargs)
            return request.respond(result)
        except Exception as e:
            response = request.error_respond(error=e)
            return response
