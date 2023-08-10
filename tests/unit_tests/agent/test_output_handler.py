import pytest
from unittest.mock import Mock, patch, MagicMock

from superagi.agent.common_types import ToolExecutorResponse
from superagi.agent.output_handler import ToolOutputHandler, TaskOutputHandler, ReplaceTaskOutputHandler
from superagi.agent.output_parser import AgentSchemaOutputParser, AgentGPTAction
from superagi.agent.task_queue import TaskQueue
from superagi.agent.tool_executor import ToolExecutor
from superagi.helper.json_cleaner import JsonCleaner
from superagi.models.agent import Agent
from superagi.models.agent_execution_permission import AgentExecutionPermission


# Test for ToolOutputHandler
@patch.object(TaskQueue, 'complete_task')
@patch.object(TaskQueue, 'get_tasks')
@patch.object(TaskQueue, 'get_completed_tasks')
@patch.object(AgentSchemaOutputParser, 'parse')
def test_tool_output_handle(parse_mock, execute_mock, get_completed_tasks_mock, complete_task_mock):
    # Arrange
    agent_execution_id = 11
    agent_config = {"agent_id": 22, "permission_type": "unrestricted"}
    assistant_reply = '{"tool": {"name": "someAction", "args": ["arg1", "arg2"]}}'
    parse_mock.return_value = AgentGPTAction(name="someAction", args=["arg1", "arg2"])

    # Define what the mock response status should be
    execute_mock.return_value = Mock(status='PENDING', is_permission_required=False)

    handler = ToolOutputHandler(agent_execution_id, agent_config, [])

    # Mock session
    session_mock = MagicMock()
    session_mock.query.return_value.filter.return_value.first.return_value = Mock()
    handler._check_for_completion = Mock(return_value=Mock(status='PENDING', is_permission_required=False))
    handler.handle_tool_response = Mock(return_value=Mock(status='PENDING', is_permission_required=False))
    # Act
    response = handler.handle(session_mock, assistant_reply)

    # Assert
    assert response.status == "PENDING"
    parse_mock.assert_called_with(assistant_reply)
    assert session_mock.add.call_count == 2

@patch('superagi.models.agent_execution_permission.AgentExecutionPermission')
def test_tool_handler_check_permission_in_restricted_mode(op_mock):
    # Mock the session
    session_mock = MagicMock()

    # Arrange
    agent_execution_id = 1
    agent_config = {"agent_id": 2, "permission_type": "RESTRICTED"}
    assistant_reply = '{"tool": {"name": "someAction", "args": ["arg1", "arg2"]}}'
    op_mock.parse.return_value = AgentGPTAction(name="someAction", args=["arg1", "arg2"])
    tool = MagicMock()
    tool.name = "someAction"
    tool.permission_required = True
    handler = ToolOutputHandler(agent_execution_id, agent_config, [tool])

    # Act
    response = handler._check_permission_in_restricted_mode(session_mock, assistant_reply)

    # Assert
    assert response.is_permission_required
    assert response.status == "WAITING_FOR_PERMISSION"
    session_mock.add.assert_called_once()
    session_mock.commit.assert_called_once()


# Test for TaskOutputHandler
@patch.object(TaskQueue, 'add_task')
@patch.object(TaskQueue, 'get_tasks')
@patch.object(JsonCleaner, 'extract_json_array_section')
def test_task_output_handle_method(extract_json_array_section_mock, get_tasks_mock, add_task_mock):
    # Arrange
    agent_execution_id = 1
    agent_config = {"agent_id": 2}
    assistant_reply = '["task1", "task2", "task3"]'
    tasks = ["task1", "task2", "task3"]
    extract_json_array_section_mock.return_value = str(tasks)
    get_tasks_mock.return_value = tasks
    handler = TaskOutputHandler(agent_execution_id, agent_config)

    # Mock session
    session_mock = MagicMock()

    # Act
    response = handler.handle(session_mock, assistant_reply)

    # Assert
    extract_json_array_section_mock.assert_called_once_with(assistant_reply)
    assert add_task_mock.call_count == len(tasks)
    assert session_mock.add.call_count == len(tasks)
    get_tasks_mock.assert_called_once()
    assert response.status == "PENDING"


# Test for ReplaceTaskOutputHandler
@patch.object(TaskQueue, 'clear_tasks')
@patch.object(TaskQueue, 'add_task')
@patch.object(TaskQueue, 'get_tasks')
@patch.object(JsonCleaner, 'extract_json_array_section')
def test_handle_method(extract_json_array_section_mock, get_tasks_mock, add_task_mock, clear_tasks_mock):
    # Arrange
    agent_execution_id = 1
    agent_config = {}
    assistant_reply = '["task1", "task2", "task3"]'
    tasks = ["task1", "task2", "task3"]
    extract_json_array_section_mock.return_value = str(tasks)
    get_tasks_mock.return_value = tasks
    handler = ReplaceTaskOutputHandler(agent_execution_id, agent_config)

    # Mock session
    session_mock = MagicMock()

    # Act
    response = handler.handle(session_mock, assistant_reply)

    # Assert
    extract_json_array_section_mock.assert_called_once_with(assistant_reply)
    clear_tasks_mock.assert_called_once()
    assert add_task_mock.call_count == len(tasks)
    get_tasks_mock.assert_called_once()
    assert response.status == "PENDING"
