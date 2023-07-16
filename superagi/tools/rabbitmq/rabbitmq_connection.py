import pika
import logging
from pika.exceptions import AMQPConnectionError

class RabbitMQConnection:
    def __init__(self, connection_params, action, queue_name=None, message=None, persistent=False, priority=0, callback=None, consumer_tag=None, delivery_tag=None):
        self.connection_params = connection_params
        self.action = action
        self.queue_name = queue_name
        self.message = message
        self.persistent = persistent
        self.priority = priority
        self.logger = logging.getLogger(__name__)

    def on_connected(self, connection):
        self.connection = connection
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        if self.action == 'add_consumer':
            self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
        elif self.action == 'remove_consumer':
            self.channel.basic_cancel(self.consumer_tag)
        elif self.action == 'send_ack':
            self.channel.basic_ack(self.delivery_tag)
        elif self.action == 'send':
            properties = pika.BasicProperties(priority=self.priority)
            self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=self.message, properties=properties)

    def on_message(self, channel, method, properties, body):
        if self.callback:
            self.callback(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        try:
            self.connection = pika.SelectConnection(
                self.connection_params,
                on_open_callback=self.on_connected,
                on_close_callback=self.on_close
            )
            try:
                self.connection.ioloop.start()
            except KeyboardInterrupt:
                self.connection.close()
                self.connection.ioloop.start()
        except AMQPConnectionError as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {str(e)}")

    def on_close(self, connection, reason):
        if isinstance(reason, pika.exceptions.AMQPConnectionError):
            self.logger.error('Failed to connect to RabbitMQ')
        elif isinstance(reason, pika.exceptions.AMQPChannelError):
            self.logger.error('An error occurred with the channel')
