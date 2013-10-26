#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import gevent

from . import RPCServer


class RPCServerGreenlets(RPCServer):
    # documentation in docs because of dependencies
    def _spawn(self, func, *args, **kwargs):
        gevent.spawn(func, *args, **kwargs)

    def start(self):
        '''
        Create a Greenlet with serve_forever so you can do a gevenet.joinall of 
        several RPCServerGreenlets  
        '''
        return gevent.spawn(self.serve_forever)