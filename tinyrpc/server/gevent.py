#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Server definition.

Defines and implements a single-threaded, single-process, asynchronous server.
"""

import gevent

from . import RPCServer


class RPCServerGreenlets(RPCServer):
    """Asynchronous RPCServer.

    This implementation of :py:class:`~tinyrpc.server.RPCServer` uses
    :py:func:`gevent.spawn` to spawn new client handlers, resulting
    in asynchronous handling of clients using greenlets.
    """

    def _spawn(self, func, *args, **kwargs):
        """Spawn a handler function.

        Spawns the supplied ``func`` with ``*args`` and ``**kwargs``
        as a gevent greenlet.

        :param func: A callable to call.
        :param args: Arguments to ``func``.
        :param kwargs: Keyword arguments to ``func``.
        """
        gevent.spawn(func, *args, **kwargs)

    def start(self):
        '''
        Create a Greenlet with serve_forever so you can do a gevenet.joinall of 
        several RPCServerGreenlets  
        '''
        return gevent.spawn(self.serve_forever)