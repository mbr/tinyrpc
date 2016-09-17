#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import gevent
    import gevent.monkey

    gevent.monkey.patch_all()
    from collections import namedtuple
    HAS_GEVENT = True
except:
    HAS_GEVENT = False

from .exc import RPCError

if HAS_GEVENT:
    RPCCall = namedtuple('RPCCall', 'method args kwargs')
    """Defines the elements of a RPC call.

    RPCCall is used with ``call_all`` to provide the list of
    requests to be processed. Each request contains the three elements
    defined in this tuple.
    """

class RPCClient(object):
    """Client for making RPC calls to connected servers.

    :param protocol: An :py:class:`~tinyrpc.RPCProtocol` instance.
    :param transport: A :py:class:`~tinyrpc.transports.ClientTransport`
                      instance.
    """

    def __init__(self, protocol, transport):
        self.protocol = protocol
        self.transport = transport

    def _send_and_handle_reply(self, req, one_way):
        # sends ...
        reply = self.transport.send_message(req.serialize())

        if one_way:
            # ... and be done
            return

        # ... or waits for reply
        response = self.protocol.parse_reply(reply)

        if hasattr(response, 'error'):
            raise RPCError('Error calling remote procedure: %s' %\
                           response.error)

        return response

    def call(self, method, args, kwargs, one_way=False):
        """Calls the requested method and returns the result.

        If an error occured, an :py:class:`~tinyrpc.exc.RPCError` instance
        is raised.

        :param method: Name of the method to call.
        :param args: Arguments to pass to the method.
        :param kwargs: Keyword arguments to pass to the method.
        :param one_way: Whether or not a reply is desired.
        """
        req = self.protocol.create_request(method, args, kwargs, one_way)

        rep = self._send_and_handle_reply(req, one_way)

        if one_way:
            return

        return rep.result

    if HAS_GEVENT:
        def call_all(self, requests, one_way=False):
            """Calls all requests from greenlets thus parallelizing fan-out.

            When the gevent module is present ``call_all`` is defined. It takes a
            list of requests and processes them in parallel returning a list of results.

            :param requests: List of RPCCall tuples containing the requests to make.
            :param one_way: Whether or not the requests generate replies.
            """
            reqs = [self.protocol.create_request(r.method, r.args, r.kwargs, one_way) for r in requests]
            threads = [gevent.spawn(self._send_and_handle_reply, r, one_way) for r in reqs]
            gevent.joinall(threads)
            return [t.value for t in threads]
    else:
        def call_all(self, requests, one_way=False):
            raise NotImplemented

    def get_proxy(self, prefix='', one_way=False):
        """Convenience method for creating a proxy.

        :param prefix: Passed on to :py:class:`~tinyrpc.client.RPCProxy`.
        :param one_way: Passed on to :py:class:`~tinyrpc.client.RPCProxy`.
        :return: :py:class:`~tinyrpc.client.RPCProxy` instance."""
        return RPCProxy(self, prefix, one_way)

    def batch_call(self, calls):
        """Experimental, use at your own peril."""
        req = self.protocol.create_batch_request()

        for call_args in calls:
            req.append(self.protocol.create_request(*call_args))

        return self._send_and_handle_reply(req)


class RPCProxy(object):
    """Create a new remote proxy object.

    Proxies allow calling of methods through a simpler interface. See the
    documentation for an example.

    :param client: An :py:class:`~tinyrpc.client.RPCClient` instance.
    :param prefix: Prefix to prepend to every method name.
    :param one_way: Passed to every call of
                    :py:func:`~tinyrpc.client.call`.
    """

    def __init__(self, client, prefix='', one_way=False):
        self.client = client
        self.prefix = prefix
        self.one_way = one_way

    def __getattr__(self, name):
        """Returns a proxy function that, when called, will call a function
        name ``name`` on the client associated with the proxy.
        """
        proxy_func = lambda *args, **kwargs: self.client.call(
                         self.prefix + name,
                         args,
                         kwargs,
                         one_way=self.one_way
                     )
        return proxy_func
