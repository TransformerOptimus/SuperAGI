# rabbitmq_tool.py
from pika.exceptions import AMQPConnectionError
import os
import json
import datetime
import pika
import logging
from abc import ABC
from typing import Type, Optional, Any
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from rabbitmq_connection import RabbitMQConnection

class RabbitMQTool(BaseTool, BaseModel):
    logger: Any
    name: str = "RabbitMQTool"
    description: str = "Tool that contains various operations to interact with RabbitMQ"

    rabbitmq_server: str = Field(default_factory=lambda: os.getenv('RABBITMQ_SERVER', 'localhost'))
    rabbitmq_username: str = Field(default_factory=lambda: os.getenv('RABBITMQ_USERNAME', 'guest'))
    rabbitmq_password: str = Field(default_factory=lambda: os.getenv('RABBITMQ_PASSWORD', 'guest'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)

    def build_connection_params(self):
        self.logger.debug("Building connection params.")
        credentials = pika.PlainCredentials(self.rabbitmq_username, self.rabbitmq_password)
        self.logger.debug("Connection params built.")
        return pika.ConnectionParameters(host=self.rabbitmq_server, credentials=credentials)

    # rest of the code is the same

    def build_connection_params(self):
        credentials = pika.PlainCredentials(self.rabbitmq_username, self.rabbitmq_password)
        return pika.ConnectionParameters(host=self.rabbitmq_server, credentials=credentials)

    def _execute(self, *args, **kwargs):
        tool_input = kwargs.get("tool_input", {})
        if isinstance(tool_input, str):
            try:
                tool_input = json.loads(tool_input)
            except json.JSONDecodeError:
                tool_input = {"operation": "send_message", "receiver": "Linda", "message": tool_input}
        
        operation = tool_input.get("operation")
        if operation == "send_message":
            receiver = tool_input.get("receiver")
            message = tool_input.get("message")
            return self._execute_send(receiver, message)
        elif operation == "receive_message":
            queue_name = tool_input.get("queue_name")
            return self._execute_receive(queue_name)
        else:
            raise ValueError(f"Unknown operation: '{operation}'")

    def _execute_send(self, receiver, message, persistent=False, priority=0):
        try:
            connection_params = self.build_connection_params()
            connection = RabbitMQConnection(connection_params, "send", receiver, message, persistent, priority)
            return connection.run()
        except (AMQPConnectionError, AMQPChannelError) as e:
            self.logger.error(f"Error while sending message: {str(e)}")
            return None

    def _execute_receive(self, queue_name):
        try:
            connection_params = self.build_connection_params()
            connection = RabbitMQConnection(connection_params, "receive", queue_name)
            return connection.run()
        except (AMQPConnectionError, AMQPChannelError) as e:
            self.logger.error(f"Error while receiving message: {str(e)}")
            return None

    def send_message(self, receiver, message, msg_type="text", priority=0):
        message = {
            "sender": self.name,
            "receiver": receiver,
            "timestamp": datetime.datetime.now().isoformat(),
            "type": msg_type,
            "content": message
        }
        tool_input = {
            "operation": "send_message",
            "receiver": receiver,
            "message": json.dumps(message)
        }
        return self._execute(tool_input=tool_input)

    def receive_message(self, queue_name):
        tool_input = {
            "operation": "receive_message",
            "queue_name": queue_name
        }
        raw_message = self._execute(tool_input=tool_input)
        message = json.loads(raw_message)
        return message["content"]
