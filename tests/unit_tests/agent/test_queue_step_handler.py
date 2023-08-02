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


@pytest.fixture
def step_tool():
    step_tool = Mock()
    step_tool.unique_id = "unique_id"
    step_tool.input_instruction = "input_instruction"
    return step_tool


def test_queue_identifier(queue_step_handler):
    step_tool = Mock()
    step_tool.unique_id = "step_id"
    assert queue_step_handler._queue_identifier(step_tool) == "step_id_1"


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


@patch("superagi.agent.queue_step_handler.TaskQueue")
@patch("superagi.agent.queue_step_handler.AgentExecutionFeed")
def test_add_to_queue(task_queue_mock, agent_execution_feed_mock, queue_step_handler, step_tool):
    # Setup mocks
    queue_step_handler._process_input_instruction = Mock(return_value='{"reply": ["task1", "task2"]}')
    queue_step_handler._process_reply = Mock()

    # Call the method
    queue_step_handler._add_to_queue(task_queue_mock, step_tool)

    # Verify the calls
    queue_step_handler._process_input_instruction.assert_called_once_with(step_tool)
    queue_step_handler._process_reply.assert_called_once_with(task_queue_mock, '{"reply": ["task1", "task2"]}')


@patch("superagi.agent.queue_step_handler.TaskQueue")
@patch("superagi.agent.queue_step_handler.AgentExecutionFeed")
def test_consume_from_queue(task_queue_mock, agent_execution_feed_mock, queue_step_handler, step_tool):
    # Setup mocks
    task_queue_mock.get_tasks.return_value = ['task1', 'task2']
    task_queue_mock.get_first_task.return_value = 'task1'
    agent_execution_feed_instance = agent_execution_feed_mock.return_value

    # Call the method
    queue_step_handler._consume_from_queue(task_queue_mock)

    # Verify the calls
    queue_step_handler.session.commit.assert_called()  # Ensure session commits were called
    queue_step_handler.session.add.assert_called()
    task_queue_mock.complete_task.assert_called_once_with("PROCESSED")
