import pytest
from unittest.mock import Mock, patch
from superagi.agent.queue_step_handler import QueueStepHandler


# To prevent having to patch each time, setup a pytest fixture
@pytest.fixture
def queue_step_handler():
    # Mock dependencies
    session = Mock()
    llm = Mock()
    agent_id = 1
    agent_execution_id = 1

    # Instantiate your class with the mocked dependencies
    return QueueStepHandler(session, llm, agent_id, agent_execution_id)


def test_queue_identifier(queue_step_handler):
    step_tool = Mock()
    step_tool.unique_id = "step_id"
    assert queue_step_handler.queue_identifier(step_tool) == "step_id_1"


@patch("superagi.agent.queue_step_handler.AgentExecution")  # Replace with your actual module path
@patch("superagi.agent.queue_step_handler.AgentWorkflowStep")
@patch("superagi.agent.queue_step_handler.AgentWorkflowStepTool")
@patch("superagi.agent.queue_step_handler.TaskQueue")
def test_execute_step(task_queue_mock, agent_execution_mock, workflow_step_mock, step_tool_mock, queue_step_handler):
    agent_execution_mock.get_agent_execution_from_id.return_value = Mock(current_agent_step_id="step_id")
    workflow_step_mock.find_by_id.return_value = Mock(action_reference_id="action_id")
    step_tool_mock.find_by_id.return_value = Mock()
    task_queue_mock.return_value.get_status.return_value = None  # Mock the get_status method on TaskQueue

    # Here you can add assertions depending on what you expect
    # For example if you expect the return value to be "default", you could do
    assert queue_step_handler.execute_step() == "default"


@patch("superagi.agent.queue_step_handler.AgentExecution")
@patch("superagi.agent.queue_step_handler.AgentExecutionFeed")
@patch("superagi.agent.queue_step_handler.TaskQueue")
def test_consume_from_queue(task_queue_mock, agent_execution_feed_mock, agent_execution_mock, queue_step_handler):
    step_tool = Mock()
    step_tool.unique_id = "unique_id"
    agent_execution_mock.find_by_id.return_value = Mock()
    task_queue_mock.return_value.get_tasks.return_value = ['task1', 'task2']  # Mock the tasks returned from the queue
    task_queue_mock.return_value.get_first_task.return_value = 'task1'  # Mock the first task in the queue
    agent_execution_feed_instance = agent_execution_feed_mock.return_value  # Get the instance of the mock
    agent_execution_feed_instance.feed = 'task1'  # Set the value of the feed property
    agent_execution_feed_instance.agent_id = queue_step_handler.agent_id
    agent_execution_feed_instance.agent_execution_id = queue_step_handler.agent_execution_id

    # Here you can add assertions depending on what you expect
    queue_step_handler.consume_from_queue(step_tool)

    # Verify that a task response feed was added to the session
    assert queue_step_handler.session.add.called
    added_feed = queue_step_handler.session.add.call_args[0][0]
    assert added_feed.feed == 'task1'
    assert added_feed.agent_id == queue_step_handler.agent_id
    assert added_feed.agent_execution_id == queue_step_handler.agent_execution_id

    # Verify that the first task was marked as processed
    task_queue_mock.return_value.complete_task.assert_called_with("PROCESSED")


@patch("superagi.agent.queue_step_handler.AgentWorkflowStepTool")
@patch("superagi.agent.queue_step_handler.JsonCleaner.extract_json_array_section")
@patch("superagi.agent.queue_step_handler.TaskQueue")
def test_add_to_queue(task_queue_mock, json_cleaner_mock, step_tool_mock, queue_step_handler):
    step_tool = Mock()
    step_tool.unique_id = "unique_id"
    json_cleaner_mock.return_value = '["task1", "task2"]'  # Mock the JsonCleaner return value
    queue_step_handler._process_input_instruction = Mock(
        return_value='["task1", "task2"]')  # Mock the _process_input_instruction method
    # queue_step_handler._process_reply = Mock()  # Do not mock _process_reply

    # Here you can add assertions depending on what you expect
    queue_step_handler.add_to_queue(step_tool)

    # Check if _process_input_instruction and _process_reply are called with expected arguments
    queue_step_handler._process_input_instruction.assert_called_with(step_tool)
    # queue_step_handler._process_reply.assert_called_with(step_tool, '["task1", "task2"]')

    # If you want to check whether the add_task of TaskQueue is called with expected arguments, you can add the following checks:
    task_queue_instance = task_queue_mock.return_value  # Get the instance of the mock
    task_queue_instance.add_task.assert_any_call("task1")
    task_queue_instance.add_task.assert_any_call("task2")
