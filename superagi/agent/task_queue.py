import json
import ast

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
        self.db.lpush(self.completed_tasks, json.dumps({"task": task, "response": response}))

    def get_first_task(self):
        return self.db.lindex(self.queue_name, 0)

    def get_tasks(self):
        return self.db.lrange(self.queue_name, 0, -1)

    def get_completed_tasks(self):
        tasks = self.db.lrange(self.completed_tasks, 0, -1)
        parsed_tasks = []
        for task in tasks:
            parsed_task = self._parse_task_record(task)
            if parsed_task is not None:
                parsed_tasks.append(parsed_task)
        return parsed_tasks

    def clear_tasks(self):
        self.db.delete(self.queue_name)

    def get_last_task_details(self):
        response = self.db.lindex(self.completed_tasks, 0)
        if response is None:
            return None

        return self._parse_task_record(response)

    @staticmethod
    def _parse_task_record(raw_task):
        try:
            parsed_task = json.loads(raw_task)
        except json.JSONDecodeError:
            try:
                parsed_task = ast.literal_eval(raw_task)
            except (ValueError, SyntaxError):
                return None

        if isinstance(parsed_task, dict):
            return parsed_task
        return None

    def set_status(self, status):
        self.db.set(self.queue_name + "_status", status)

    def get_status(self):
        return self.db.get(self.queue_name + "_status")

