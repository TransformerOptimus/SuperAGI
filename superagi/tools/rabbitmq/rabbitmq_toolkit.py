from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool
import pika
import os
import logging
from .rabbitmq_connection import RabbitMQConnection

class RabbitMQToolkit(BaseTool, ABC):
    name = "RabbitMQ Toolkit"
    description = "A tool for interacting with RabbitMQ"

    def __init__(self):
        self.rabbitmq_server = os.getenv('RABBITMQ_SERVER', 'localhost')
        self.rabbitmq_username = os.getenv('RABBITMQ_USERNAME', 'guest')
        self.rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.connection_params = pika.ConnectionParameters(
            host=self.rabbitmq_server,
            credentials=pika.PlainCredentials(self.rabbitmq_username, self.rabbitmq_password)
        )
        self.logger = logging.getLogger(__name__)

    def execute(self, action, queue_name, message=None, persistent=False):
        """
        Execute a RabbitMQ operation.
        
        The operation can be either "send", "receive", "create_queue", or "delete_queue". 
        If the operation is "send", a message is sent to the specified queue. 
        If the operation is "receive", a message is received from the specified queue.
        If the operation is "create_queue", a new queue is created with the specified name.
        If the operation is "delete_queue", the specified queue is deleted.
        """
        connection = RabbitMQConnection(self.connection_params, action, queue_name, message, persistent)
        connection.run()

    def get_env_keys(self) -> List[str]:
        return ['RABBITMQ_SERVER', 'RABBITMQ_USERNAME', 'RABBITMQ_PASSWORD']
