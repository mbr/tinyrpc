from tinyrpc.client import RPCClient, RPCError


class AsyncRPCClient(RPCClient):
    """
    Async version of tinyrpc.RPCClient
    """

    async def _send_and_handle_reply(self, req, one_way, transport=None,
                                     no_exception=False):
        tport = self.transport if transport is None else transport

        # sends ...
        reply = await tport.send_message(req.serialize())

        if one_way:
            # ... and be done
            return

        # ... or process the reply
        response = self.protocol.parse_reply(reply)

        if not no_exception and hasattr(response, 'error'):
            raise RPCError('Error calling remote procedure: %s' %
                           response.error)

        return response

    async def call(self, method, args, kwargs, one_way=False):
        req = self.protocol.create_request(method, args, kwargs, one_way)

        rep = await self._send_and_handle_reply(req, one_way)

        if one_way:
            return

        return rep.result
