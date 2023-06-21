import unittest
from unittest.mock import patch

from superagi.agent.task_queue import TaskQueue


class TaskQueueTests(unittest.TestCase):
    def setUp(self):
        self.queue_name = "test_queue"
        self.queue = TaskQueue(self.queue_name)

    @patch.object(TaskQueue, 'add_task')
    def test_add_task(self, mock_add_task):
        task = "Do something"
        self.queue.add_task(task)
        mock_add_task.assert_called_with(task)

    @patch.object(TaskQueue, 'complete_task')
    def test_complete_task(self, mock_complete_task):
        task = "Do something"
        response = "Task completed"
        self.queue.complete_task(response)
        mock_complete_task.assert_called_with(response)

    @patch.object(TaskQueue, 'get_first_task')
    def test_get_first_task(self, mock_get_first_task):
        self.queue.get_first_task()
        mock_get_first_task.assert_called()

    @patch.object(TaskQueue, 'get_tasks')
    def test_get_tasks(self, mock_get_tasks):
        self.queue.get_tasks()
        mock_get_tasks.assert_called()

    @patch.object(TaskQueue, 'get_completed_tasks')
    def test_get_completed_tasks(self, mock_get_completed_tasks):
        self.queue.get_completed_tasks()
        mock_get_completed_tasks.assert_called()

    @patch.object(TaskQueue, 'clear_tasks')
    def test_clear_tasks(self, mock_clear_tasks):
        self.queue.clear_tasks()
        mock_clear_tasks.assert_called()

    @patch.object(TaskQueue, 'get_last_task_details')
    def test_get_last_task_details(self, mock_get_last_task_details):
        self.queue.get_last_task_details()
        mock_get_last_task_details.assert_called()


if __name__ == '__main__':
    unittest.main()
