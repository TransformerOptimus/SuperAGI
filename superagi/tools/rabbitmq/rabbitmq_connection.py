import pika
import logging

class RabbitMQConnection:
    def __init__(self, connection_params, action, queue_name, message, persistent):
        self.connection_params = connection_params
        self.action = action
        self.queue_name = queue_name
        self.message = message
        self.persistent = persistent
        self.logger = logging.getLogger(__name__)

    def on_connected(self, connection):
        # Called when the toolkit has successfully connected to RabbitMQ
        # TODO: Add code to perform the specified operation using the connection

    def on_closed(self, connection, reason):
        # Called when the toolkit's connection to RabbitMQ has been closed

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
