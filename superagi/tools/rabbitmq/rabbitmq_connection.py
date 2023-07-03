import pika
import logging

class RabbitMQConnection:
    def __init__(self, connection_params, action, queue_name, message, persistent, priority, callback=None, consumer_tag=None, delivery_tag=None):
        self.connection_params = connection_params
        self.action = action
        self.queue_name = queue_name
        self.message = message
        self.persistent = persistent
        self.priority = priority
        self.callback = callback
        self.consumer_tag = consumer_tag
        self.delivery_tag = delivery_tag
        self.logger = logging.getLogger(__name__)

    def on_connected(self, connection):
        if self.action == 'add_consumer':
            self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
        elif self.action == 'remove_consumer':
            self.channel.basic_cancel(self.consumer_tag)
        elif self.action == 'send_ack':
            self.channel.basic_ack(self.delivery_tag)
        elif self.action == 'send':
            properties = pika.BasicProperties(priority=self.priority)
            self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=self.message, properties=properties)
        # ... rest of the method ...

    def on_message(self, channel, method, properties, body):
        # Call the callback function with the message body
        self.callback(body)

        # Send an acknowledgement
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def on_closed(self, connection, reason):
        if isinstance(reason, pika.exceptions.AMQPConnectionError):
            self.logger.error('Failed to connect to RabbitMQ')
        elif isinstance(reason, pika.exceptions.AMQPChannelError):
            self.logger.error('An error occurred with the channel')
        # ... rest of the method ...

    def run(self):
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
