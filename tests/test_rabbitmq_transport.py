#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch

from tinyrpc.transports.rabbitmq import RabbitMQServerTransport, RabbitMQClientTransport

FAKE_REQUEST_MSG = b'a fake request message'
FAKE_RESPONSE_MSG = b'a fake response message'
TEST_QUEUE = 'test_queue'
TEST_ROUTE = 'test_route'

class DummyBlockingConnection:
    class DummyChannel:
        class GenericObject(object):
            pass

        def __init__(self):
            self.properties = "properties"

        def queue_declare(self, *args, **kwargs):
            result = self.GenericObject()
            result.method = self.GenericObject()
            result.method.queue = "queue_id"
            return result

        def basic_consume(self, on_message_callback, *args, **kwargs):
            self.on_message_callback = on_message_callback

        def basic_publish(self, properties, *args, **kwargs):
            self.properties = properties


    def __init__(self, *args, **kwargs):
        pass

    def channel(self):
        self.channel = self.DummyChannel()
        return self.channel

    def process_data_events(self):
        fake_response = FAKE_RESPONSE_MSG
        self.channel.on_message_callback("channel", "method", self.channel.properties, fake_response)

@pytest.fixture
def dummy_blockingconnection():
    return DummyBlockingConnection()

@pytest.fixture
def rabbitmq_server(dummy_blockingconnection):
    return RabbitMQServerTransport(dummy_blockingconnection, TEST_QUEUE)

@pytest.fixture
def rabbitmq_client(dummy_blockingconnection):
    return RabbitMQClientTransport(dummy_blockingconnection, TEST_ROUTE)

@patch('pika.BlockingConnection', DummyBlockingConnection)
def test_can_create_rabbitmq_server():
    RabbitMQServerTransport.create("localhost", TEST_QUEUE)

@patch('pika.BlockingConnection', DummyBlockingConnection)
def test_can_create_rabbitmq_client():
    RabbitMQClientTransport.create("localhost", TEST_ROUTE)

def test_server_can_receive_message(rabbitmq_server):
    context, message = rabbitmq_server.receive_message()
    assert context
    assert message == FAKE_RESPONSE_MSG

def test_client_can_send_message(rabbitmq_client):
    response = rabbitmq_client.send_message(FAKE_REQUEST_MSG, expect_reply=False)
    assert response is None

def test_client_can_send_message_and_get_reply(rabbitmq_client):
    response = rabbitmq_client.send_message(FAKE_REQUEST_MSG, expect_reply=True)
    assert response == FAKE_RESPONSE_MSG
