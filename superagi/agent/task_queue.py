import json
import ast
from typing import List, Dict, Optional, Any

import redis

from superagi.config.config import get_config
from superagi.lib.logger import logger

redis_url = get_config('REDIS_URL') or "localhost:6379"


class TaskQueue:
    """Redis-backed task queue for managing agent tasks.
    
    Manages current pending tasks and completed tasks with responses.
    Provides FIFO queue semantics for task processing.
    """
    
    def __init__(self, queue_name: str):
        """Initialize the task queue.
        
        Args:
            queue_name (str): Unique name for this task queue instance.
        """
        self.queue_name = queue_name + "_q"
        self.completed_tasks = queue_name + "_q_completed"
        try:
            self.db = redis.Redis.from_url("redis://" + redis_url + "/0", decode_responses=True)
            self.db.ping()  # Verify connection
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis at {redis_url}: {e}")
            raise

    def add_task(self, task: str) -> None:
        """Add a new task to the queue.
        
        Args:
            task (str): Task description or instruction.
        """
        try:
            self.db.lpush(self.queue_name, task)
            logger.debug(f"Added task to {self.queue_name}: {task}")
        except redis.RedisError as e:
            logger.error(f"Failed to add task: {e}")
            raise

    def complete_task(self, response: Any) -> None:
        """Mark the first task as completed with a response.
        
        Args:
            response: The response/result for the completed task.
        """
        if len(self.get_tasks()) <= 0:
            logger.warning(f"Attempted to complete task but queue is empty: {self.queue_name}")
            return
        try:
            task = self.db.lpop(self.queue_name)
            self.db.lpush(self.completed_tasks, json.dumps({"task": task, "response": response}))
            logger.debug(f"Task completed and moved to history: {self.queue_name}")
        except redis.RedisError as e:
            logger.error(f"Failed to complete task: {e}")
            raise

    def get_first_task(self) -> Optional[str]:
        """Get the first (oldest) pending task without removing it.
        
        Returns:
            str: First task in queue, or None if queue is empty.
        """
        return self.db.lindex(self.queue_name, 0)

    def get_tasks(self) -> List[str]:
        """Get all pending tasks in order.
        
        Returns:
            List[str]: List of all pending tasks.
        """
        return self.db.lrange(self.queue_name, 0, -1)

    def get_completed_tasks(self) -> List[Dict[str, Any]]:
        """Get all completed tasks with their responses.
        
        Returns:
            List[Dict]: List of completed task records with task and response.
        """
        tasks = self.db.lrange(self.completed_tasks, 0, -1)
        parsed_tasks = []
        for task in tasks:
            parsed_task = self._parse_task_record(task)
            if parsed_task is not None:
                parsed_tasks.append(parsed_task)
        return parsed_tasks

    def clear_tasks(self) -> None:
        """Remove all pending tasks from the queue."""
        try:
            self.db.delete(self.queue_name)
            logger.info(f"Cleared all tasks from {self.queue_name}")
        except redis.RedisError as e:
            logger.error(f"Failed to clear tasks: {e}")
            raise

    def get_last_task_details(self) -> Optional[Dict[str, Any]]:
        """Get the most recent completed task with its response.
        
        Returns:
            Dict: Task record with 'task' and 'response' keys, or None if no completed tasks.
        """
        response = self.db.lindex(self.completed_tasks, 0)
        if response is None:
            return None
        return self._parse_task_record(response)

    @staticmethod
    def _parse_task_record(raw_task: str) -> Optional[Dict[str, Any]]:
        """Parse a task record from JSON or literal Python notation.
        
        Args:
            raw_task (str): Raw task record string.
            
        Returns:
            Dict: Parsed task record, or None if parsing fails.
        """
        try:
            parsed_task = json.loads(raw_task)
        except json.JSONDecodeError:
            try:
                parsed_task = ast.literal_eval(raw_task)
            except (ValueError, SyntaxError):
                logger.warning(f"Failed to parse task record: {raw_task}")
                return None

        if isinstance(parsed_task, dict):
            return parsed_task
        return None

    def set_status(self, status: str) -> None:
        """Set the queue processing status.
        
        Args:
            status (str): Status string (e.g., 'running', 'idle', 'paused').
        """
        try:
            self.db.set(self.queue_name + "_status", status)
            logger.debug(f"Queue status updated to: {status}")
        except redis.RedisError as e:
            logger.error(f"Failed to set queue status: {e}")
            raise

    def get_status(self) -> Optional[str]:
        """Get the current queue processing status.
        
        Returns:
            str: Current status, or None if not set.
        """
        return self.db.get(self.queue_name + "_status")

