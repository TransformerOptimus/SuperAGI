from unittest.mock import Mock, patch, MagicMock

import pytest

from superagi.agent.agent_iteration_step_handler import AgentIterationStepHandler
from superagi.agent.agent_message_builder import AgentLlmMessageBuilder
from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.agent.output_handler import ToolOutputHandler
from superagi.agent.task_queue import TaskQueue
from superagi.agent.tool_builder import ToolBuilder
from superagi.config.config import get_config
from superagi.helper.token_counter import TokenCounter
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.agent_execution_permission import AgentExecutionPermission
from superagi.models.organisation import Organisation
from superagi.models.tool import Tool
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.iteration_workflow import IterationWorkflow
from superagi.models.workflows.iteration_workflow_step import IterationWorkflowStep
from superagi.resource_manager.resource_summary import ResourceSummarizer
from superagi.tools.code.write_code import CodingTool
from superagi.tools.resource.query_resource import QueryResourceTool
from superagi.tools.thinking.tools import ThinkingTool


# Given
@pytest.fixture
def test_handler():
    mock_session = Mock()
    llm = Mock()
    agent_id = 1
    agent_execution_id = 1

    # Creating an instance of the class to test
    handler = AgentIterationStepHandler(mock_session, llm, agent_id, agent_execution_id)
    return handler

def test_build_agent_prompt(test_handler, mocker):
    # Arrange
    iteration_workflow = IterationWorkflow(has_task_queue=True)
    agent_config = {'constraints': 'Test constraint'}
    agent_execution_config = {'goal': 'Test goal', 'instruction': 'Test instruction'}
    prompt = 'Test prompt'
    task_queue = TaskQueue(queue_name='Test queue')
    agent_tools = []

    mocker.patch.object(AgentPromptBuilder, 'replace_main_variables', return_value='Test prompt')
    mocker.patch.object(AgentPromptBuilder, 'replace_task_based_variables', return_value='Test prompt')
    mocker.patch.object(task_queue, 'get_last_task_details', return_value={"task": "last task", "response": "last response"})
    mocker.patch.object(task_queue, 'get_first_task', return_value='Test task')
    mocker.patch.object(task_queue, 'get_tasks', return_value=[])
    mocker.patch.object(task_queue, 'get_completed_tasks', return_value=[])
    mocker.patch.object(TokenCounter, 'token_limit', return_value=1000)
    mocker.patch('superagi.agent.agent_iteration_step_handler.get_config', return_value=600)

    # Act
    test_handler.task_queue = task_queue
    result_prompt = test_handler._build_agent_prompt(iteration_workflow, agent_config, agent_execution_config,
                                                     prompt, agent_tools)

    # Assert
    assert result_prompt == 'Test prompt'
    AgentPromptBuilder.replace_main_variables.assert_called_once_with(prompt, agent_execution_config["goal"],
                                                                      agent_execution_config["instruction"],
                                                                      agent_config["constraints"], agent_tools, False)
    AgentPromptBuilder.replace_task_based_variables.assert_called_once()
    task_queue.get_last_task_details.assert_called_once()
    task_queue.get_first_task.assert_called_once()
    task_queue.get_tasks.assert_called_once()
    task_queue.get_completed_tasks.assert_called_once()
    TokenCounter.token_limit.assert_called_once()

def test_build_tools(test_handler, mocker):
    # Arrange
    agent_config = {'model': 'gpt-3', 'tools': [1, 2, 3], 'resource_summary': True}
    agent_execution_config = {'goal': 'Test goal', 'instruction': 'Test instruction'}

    mocker.patch.object(AgentConfiguration, 'get_model_api_key', return_value='test_api_key')
    mocker.patch.object(ToolBuilder, 'build_tool')
    mocker.patch.object(ToolBuilder, 'set_default_params_tool', return_value=ThinkingTool())
    mocker.patch.object(ResourceSummarizer, 'fetch_or_create_agent_resource_summary', return_value=True)
    mocker.patch('superagi.models.tool.Tool')
    test_handler.session.query.return_value.filter.return_value.all.return_value = [ThinkingTool()]

    # Act
    agent_tools = test_handler._build_tools(agent_config, agent_execution_config)

    # Assert
    assert isinstance(agent_tools[0], ThinkingTool)
    assert ToolBuilder.build_tool.call_count == 1
    assert ToolBuilder.set_default_params_tool.call_count == 3
    assert AgentConfiguration.get_model_api_key.call_count == 1
    assert ResourceSummarizer.fetch_or_create_agent_resource_summary.call_count == 1


def test_handle_wait_for_permission(test_handler, mocker):
    # Arrange
    mock_agent_execution = mocker.Mock(spec=AgentExecution)
    mock_agent_execution.status = "WAITING_FOR_PERMISSION"
    mock_iteration_workflow_step = mocker.Mock(spec=IterationWorkflowStep)
    mock_iteration_workflow_step.next_step_id = 123
    agent_config = {'model': 'gpt-3', 'tools': [1, 2, 3]}
    agent_execution_config = {'goal': 'Test goal', 'instruction': 'Test instruction'}

    mock_permission = mocker.Mock(spec=AgentExecutionPermission)
    mock_permission.status = "APPROVED"
    mock_permission.user_feedback = "Test feedback"
    mock_permission.tool_name = "Test tool"
    test_handler._build_tools = Mock(return_value=[ThinkingTool()])
    test_handler.session.query.return_value.filter.return_value.first.return_value = mock_permission
    # AgentExecutionPermission.filter.return_value.first.return_value = mock_permission

    mock_tool_output = mocker.MagicMock()
    mock_tool_output.result = "Test result"
    ToolOutputHandler.handle_tool_response = Mock(return_value=mock_tool_output)

    # Act
    result = test_handler._handle_wait_for_permission(
        mock_agent_execution, agent_config, agent_execution_config, mock_iteration_workflow_step)

    # Assert
    test_handler._build_tools.assert_called_once_with(agent_config, agent_execution_config)
    ToolOutputHandler.handle_tool_response.assert_called_once()
    assert mock_agent_execution.status == "RUNNING"
    assert result

