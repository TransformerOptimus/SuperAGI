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


# Security regression: _process_reply must not execute code embedded in the model
# reply. A prompt-injected/adversarial model can return a string that is a valid
# Python *expression* (e.g. a call to os.system); the queue step must reject it as a
# non-literal instead of evaluating it.
def test_process_reply_rejects_code_execution(queue_step_handler):
    task_queue_mock = Mock()
    # Payload that, under eval(), would invoke os.system and run a command.
    malicious_reply = "[__import__('os').system('echo pwned')]"

    with patch('os.system') as os_system_mock:
        with pytest.raises(ValueError):
            queue_step_handler._process_reply(task_queue_mock, malicious_reply)
        os_system_mock.assert_not_called()

    # No task should have been added from the malicious payload.
    task_queue_mock.add_task.assert_not_called()


def test_process_reply_parses_literal_array(queue_step_handler):
    # A legitimate model reply (a literal list of task strings) must still be parsed
    # and enqueued, including the single-quoted str(dict)-style form OpenAI emits.
    task_queue_mock = Mock()
    queue_step_handler._process_reply(task_queue_mock, "['task1', 'task2']")
    assert task_queue_mock.add_task.call_count == 2


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
