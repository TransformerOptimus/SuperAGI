import os
from confluent_kafka import Producer, Consumer, KafkaError

import redis

from superagi.config.config import get_config
# Message broker connection parameters
class KafkaBroker:

  def __int__(self):
    self.broker_bootstrap_servers = get_config("BROKER_BOOTSTRAP_SERVERS", "localhost:9092")
    self.group_id = 'agent-group'

  def push_message(self, topic, message):
    # Kafka producer configuration
    producer_config = {'bootstrap.servers': self.broker_bootstrap_servers}

    # Create the Kafka producer
    producer = Producer(producer_config)

    # Produce the message to the topic
    producer.produce(topic, value=message)
    producer.flush()

  def start_listener(self, topic, on_message_received):
    # Kafka consumer configuration
    consumer_config = {
      'bootstrap.servers': self.broker_bootstrap_servers,
      'group.id': self.group_id,
      'auto.offset.reset': 'earliest'
    }

    # Create the Kafka consumer
    consumer = Consumer(consumer_config)

    # Subscribe to the topic
    consumer.subscribe([topic])

    print("Waiting for messages. To exit, press CTRL+C")

    # Start consuming messages
    try:
      while True:
        message = consumer.poll(timeout=1.0)
        if message is None:
          continue
        if message.error():
          if message.error().code() == KafkaError._PARTITION_EOF:
            # End of partition, continue to next message
            continue
          else:
            # Log error and continue to next message
            print("Error occurred:", message.error())
            continue

        # Process the received message
        on_message_received(message)

    except KeyboardInterrupt:
      # Close the consumer upon keyboard interruption
      consumer.close()
