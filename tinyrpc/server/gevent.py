#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent

from . import RPCServer


class RPCServerGreenlets(RPCServer):
    # documentation in docs because of dependencies
    def _spawn(self, func, *args, **kwargs):
        gevent.spawn()
