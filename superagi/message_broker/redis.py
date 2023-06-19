import os

import redis
from superagi.config.config import get_config
from superagi.lib.logger import logger


# Message broker connection parameters
class RedisBroker:
  def __int__(self):
    redis_host = get_config("REDIS_HOST", "localhost")
    redis_port = get_config("REDIS_PORT", "6379")
    self.redis_client = redis.Redis(host=redis_host, port=redis_port)

  def push_message(self, topic: str, message: str):
    # Establish connection to the message broker
    self.redis_client.publish(topic, message)
    logger.info("Message sent to the broker.")

  def start_listener(self, topic: str, on_message_received: callable):
    # Subscribe to the channel
    pubsub = self.redis_client.pubsub()
    pubsub.subscribe(topic)

    logger.info("Waiting for messages. To exit, press CTRL+C")

    # Start listening for messages
    for message in pubsub.listen():
      if message['type'] == 'message':
        # Process the received message
        on_message_received(message['data'])
