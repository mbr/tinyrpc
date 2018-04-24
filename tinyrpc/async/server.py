from tinyrpc import BadRequestError
from tinyrpc.server import RPCServer


class AsyncRPCServer(RPCServer):
    """
    Override default RPCServer to implement async-await calls
    Code is identical to server.RPCServer, only async-await added
    """

    async def serve_forever(self):
        while True:
            await self.receive_one_message()

    async def receive_one_message(self):
        context, message = await self.transport.receive_message()
        if callable(self.trace):
            self.trace('-->', context, message)

        # assuming protocol is threadsafe and dispatcher is theadsafe, as
        # long as its immutable

        async def handle_message(context, message):
            try:
                request = self.protocol.parse_request(message)
            except BadRequestError as e:
                response = e.error_respond()
            else:
                caller = getattr(self.protocol, '_caller', None)
                response = await self.dispatcher.dispatch(request, caller)

            # send reply
            if response is not None:
                result = response.serialize()
                if callable(self.trace):
                    self.trace('<--', context, result)
                await self.transport.send_reply(context, result)

        await self._spawn(handle_message, context, message)

    async def _spawn(self, func, *args, **kwargs):
        await func(*args, **kwargs)
