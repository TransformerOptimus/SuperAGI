import json

import redis

from superagi.config.config import get_config

redis_url = get_config('REDIS_URL') or "localhost:6379"
"""TaskQueue manages current tasks and past tasks in Redis """
class TaskQueue:
    def __init__(self, queue_name: str):
        self.queue_name = queue_name + "_q"
        self.completed_tasks = queue_name + "_q_completed"
        self.db = redis.Redis.from_url("redis://" + redis_url + "/0", decode_responses=True)

    def add_task(self, task: str):
        self.db.lpush(self.queue_name, task)
        # print("Added task. New tasks:", str(self.get_tasks()))

    def complete_task(self, response):
        if len(self.get_tasks()) <= 0:
            return
        task = self.db.lpop(self.queue_name)
        self.db.lpush(self.completed_tasks, str({"task": task, "response": response}))

    def get_first_task(self):
        return self.db.lindex(self.queue_name, 0)

    def get_tasks(self):
        return self.db.lrange(self.queue_name, 0, -1)

    def get_completed_tasks(self):
        tasks = self.db.lrange(self.completed_tasks, 0, -1)
        return [eval(task) for task in tasks]

    def clear_tasks(self):
        self.db.delete(self.queue_name)

    def get_last_task_details(self):
        response = self.db.lindex(self.completed_tasks, 0)
        if response is None:
            return None

        return eval(response)

    def set_status(self, status):
        self.db.set(self.queue_name + "_status", status)

    def get_status(self):
        return self.db.get(self.queue_name + "_status")

