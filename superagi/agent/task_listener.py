# add task listener using redis/ should have flexibility of other queues

class TaskListener:
  def __int__(self, broker):
    self.broker = broker

  def start_listener(self, topic, on_message_received):
    self.broker.start_listener(topic, on_message_received)

  def push_message(self, topic, message):
    self.broker.push_message(topic, message)
