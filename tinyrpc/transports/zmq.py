#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import  # needed for zmq import
import zmq

from . import ServerTransport, ClientTransport


class ZmqServerTransport(ServerTransport):
    def __init__(self, socket):
        self.socket = socket

    def receive_message(self):
        msg = self.socket.recv_multipart()
        return msg[:-1], msg[-1]

    def send_reply(self, context, reply):
        self.socket.send_multipart(context + [reply])

    @classmethod
    def create(cls, zmq_context, endpoint):
        socket = zmq_context.socket(zmq.ROUTER)
        socket.bind(endpoint)
        return cls(socket)


class ZmqClientTransport(ClientTransport):
    def __init__(self, socket):
        self.socket = socket

    def send_message(self, message, expect_reply=True):
        self.socket.send(message)

        if expect_reply:
            return self.socket.recv()

    @classmethod
    def create(cls, zmq_context, endpoint):
        socket = zmq_context.socket(zmq.REQ)
        socket.connect(endpoint)
        return cls(socket)
