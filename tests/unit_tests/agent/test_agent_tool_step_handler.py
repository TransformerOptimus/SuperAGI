import json
from unittest.mock import Mock, create_autospec, patch

import pytest

from superagi.agent.agent_tool_step_handler import AgentToolStepHandler
from superagi.agent.common_types import ToolExecutorResponse
from superagi.agent.output_handler import ToolOutputHandler
from superagi.agent.tool_builder import ToolBuilder
from superagi.helper.token_counter import TokenCounter
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.agent_execution_permission import AgentExecutionPermission
from superagi.models.tool import Tool
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.agent_workflow_step_tool import AgentWorkflowStepTool
from superagi.resource_manager.resource_summary import ResourceSummarizer
from superagi.tools.code.write_code import CodingTool


# Given
@pytest.fixture
def handler():
    mock_session = Mock()
    llm = Mock()
    agent_id = 1
    agent_execution_id = 1

    # Creating an instance of the class to test
    handler = AgentToolStepHandler(mock_session, llm, agent_id, agent_execution_id)
    return handler


def test_create_permission_request(handler):
    # Arrange
    execution = Mock()
    step_tool = Mock()
    step_tool.input_instruction = "input_instruction"
    handler.session.commit = Mock()
    handler.session.flush = Mock()

    mock_permission = create_autospec(AgentExecutionPermission)
    with patch('superagi.agent.agent_tool_step_handler.AgentExecutionPermission', return_value=mock_permission) as mock_cls:
        # Act
        handler._create_permission_request(execution, step_tool)

        # Assert
        mock_cls.assert_called_once_with(
            agent_execution_id=handler.agent_execution_id,
            status="PENDING",
            agent_id=handler.agent_id,
            tool_name="WAIT_FOR_PERMISSION",
            question=step_tool.input_instruction,
            assistant_reply=""
        )
        handler.session.add.assert_called_once_with(mock_permission)
        execution.permission_id = mock_permission.id
        execution.status = "WAITING_FOR_PERMISSION"
        assert handler.session.commit.call_count == 2
        assert handler.session.flush.call_count == 1



def test_execute_step(handler):
    # Arrange
    execution = create_autospec(AgentExecution)
    workflow_step = create_autospec(AgentWorkflowStep)
    step_tool = create_autospec(AgentWorkflowStepTool)
    agent_config = {}
    agent_execution_config = {}

    with patch.object(AgentExecution, 'get_agent_execution_from_id', return_value=execution), \
        patch.object(AgentWorkflowStep, 'find_by_id', return_value=workflow_step), \
        patch.object(AgentWorkflowStepTool, 'find_by_id', return_value=step_tool), \
        patch.object(Agent, 'fetch_configuration', return_value=agent_config), \
        patch.object(AgentExecutionConfiguration, 'fetch_configuration', return_value=agent_execution_config):

        handler._handle_wait_for_permission = Mock(return_value=True)
        handler._create_permission_request = Mock()
        handler._process_input_instruction = Mock(return_value="{\"}")
        handler._build_tool_obj = Mock()
        handler._process_output_instruction = Mock(return_value="step_response")
        handler._handle_next_step = Mock()

        # Act
        tool_output_handler = Mock(spec=ToolOutputHandler)
        tool_output_handler.handle.return_value = ToolExecutorResponse(status="SUCCESS", output="final_response")

        with patch('superagi.agent.agent_tool_step_handler.ToolOutputHandler', return_value=tool_output_handler):
            # Act
            handler.execute_step()

            # Assert
            handler._handle_wait_for_permission.assert_called_once()
            handler._process_input_instruction.assert_called_once_with(agent_config, agent_execution_config, step_tool,
                                                                       workflow_step)
            handler._process_output_instruction.assert_called_once()


def test_handle_next_step_with_complete(handler):
    # Arrange
    next_step = "COMPLETE"
    execution = create_autospec(AgentExecution)

    with patch.object(AgentExecution, 'get_agent_execution_from_id', return_value=execution):
        # Act
        handler._handle_next_step(next_step)

        # Assert
        assert execution.current_agent_step_id == -1
        assert execution.status == "COMPLETED"
        handler.session.commit.assert_called_once()


def test_handle_next_step_with_next_step(handler):
    # Arrange
    next_step = create_autospec(AgentExecution)  # Mocking the next_step object
    execution = create_autospec(AgentExecution)

    with patch.object(AgentExecution, 'get_agent_execution_from_id', return_value=execution), \
        patch.object(AgentExecution, 'assign_next_step_id') as mock_assign_next_step_id:

        # Act
        handler._handle_next_step(next_step)

        # Assert
        mock_assign_next_step_id.assert_called_once_with(handler.session, handler.agent_execution_id, next_step.id)
        handler.session.commit.assert_called_once()


def test_build_tool_obj(handler):
    # Arrange
    agent_config = {"model": "model1", "resource_summary": "summary"}
    agent_execution_config = {}
    tool_name = "QueryResourceTool"
    model_api_key = "apikey"
    resource_summary = "summary"
    tool = Tool()

    with patch.object(AgentConfiguration, 'get_model_api_key', return_value=model_api_key), \
         patch.object(ToolBuilder, 'build_tool', return_value=tool), \
         patch.object(ToolBuilder, 'set_default_params_tool', return_value=tool), \
         patch.object(ResourceSummarizer, 'fetch_or_create_agent_resource_summary', return_value=resource_summary), \
         patch.object(handler.session, 'query', return_value=Mock(first=Mock(return_value=tool))):

        # Act
        result = handler._build_tool_obj(agent_config, agent_execution_config, tool_name)

        # Assert
        assert result == tool


def test_process_output_instruction(handler):
    # Arrange
    final_response = "final_response"
    step_tool = AgentWorkflowStepTool()
    workflow_step = AgentWorkflowStep()
    mock_response = {"content": "response_content"}
    mock_model = Mock()
    current_tokens = 10
    token_limit = 100

    with patch.object(handler, '_build_tool_output_prompt', return_value="prompt"), \
         patch.object(TokenCounter, 'count_message_tokens', return_value=current_tokens), \
         patch.object(TokenCounter, 'token_limit', return_value=token_limit), \
         patch.object(handler.llm, 'chat_completion', return_value=mock_response), \
         patch.object(AgentExecution, 'update_tokens'):

        # Act
        result = handler._process_output_instruction(final_response, step_tool, workflow_step)

        # Assert
        assert result == mock_response['content']


def test_build_tool_input_prompt(handler):
    # Arrange
    step_tool = AgentWorkflowStepTool()
    step_tool.tool_name = "CodingTool"
    step_tool.input_instruction = "TestInstruction"
    tool = CodingTool()
    # tool.name = "TestTool"
    # tool.description = "TestDescription"
    # tool.args = {"arg1": "val1"}
    agent_execution_config = {"goal": ["Goal1", "Goal2"]}
    mock_prompt = "{goals}{tool_name}{instruction}{tool_schema}"

    with patch('superagi.agent.agent_tool_step_handler.PromptReader.read_agent_prompt', return_value=mock_prompt), \
            patch('superagi.agent.agent_tool_step_handler.AgentPromptBuilder.add_list_items_to_string', return_value="Goal1, Goal2"):
        # Act
        result = handler._build_tool_input_prompt(step_tool, tool, agent_execution_config)

        # Assert
        result = result.replace("{goals}", "Goal1, Goal2")
        result = result.replace("{tool_name}", step_tool.tool_name)
        result = result.replace("{instruction}", step_tool.input_instruction)
        tool_schema = f"\"{tool.name}\": {tool.description}, args json schema: {json.dumps(tool.args)}"
        result = result.replace("{tool_schema}", tool_schema)

        assert """Goal1, Goal2CodingToolTestInstruction""" in result


def test_build_tool_output_prompt(handler):
    # Arrange
    step_tool = AgentWorkflowStepTool()
    step_tool.tool_name = "TestTool"
    step_tool.output_instruction = "TestInstruction"
    tool_output = "TestOutput"
    workflow_step = AgentWorkflowStep()
    expected_prompt = "TestOutputTestToolTestInstruction['option1', 'option2']"
    mock_prompt = "{tool_output}{tool_name}{instruction}{output_options}"
    step_responses = ["option1", "option2", "default"]

    with patch('superagi.agent.agent_tool_step_handler.PromptReader.read_agent_prompt', return_value=mock_prompt), \
            patch.object(handler, '_get_step_responses', return_value=step_responses):
        # Act
        result = handler._build_tool_output_prompt(step_tool, tool_output, workflow_step)

        # Assert
        expected_prompt = expected_prompt.replace("{tool_output}", tool_output)
        expected_prompt = expected_prompt.replace("{tool_name}", step_tool.tool_name)
        expected_prompt = expected_prompt.replace("{instruction}", step_tool.output_instruction)
        expected_prompt = expected_prompt.replace("{output_options}", str(step_responses))

        assert result == expected_prompt


def test_handle_wait_for_permission_approved(handler):
    # Arrange
    agent_execution = AgentExecution()
    agent_execution.status = "WAITING_FOR_PERMISSION"
    agent_execution.permission_id = 123
    workflow_step = AgentWorkflowStep()
    agent_execution_permission = AgentExecutionPermission()
    agent_execution_permission.status = "APPROVED"
    next_step = AgentWorkflowStep()

    handler.session.query.return_value.filter.return_value.first.return_value = agent_execution_permission
    handler._handle_next_step = Mock()
    AgentWorkflowStep.fetch_next_step = Mock(return_value=next_step)

    # Act
    result = handler._handle_wait_for_permission(agent_execution, workflow_step)

    # Assert
    assert result == False
    handler._handle_next_step.assert_called_once_with(next_step)
    assert agent_execution.status == "RUNNING"
    assert agent_execution.permission_id == -1


def test_handle_wait_for_permission_denied(handler):
    # Arrange
    agent_execution = AgentExecution()
    agent_execution.status = "WAITING_FOR_PERMISSION"
    agent_execution.permission_id = 123
    workflow_step = AgentWorkflowStep()
    agent_execution_permission = AgentExecutionPermission()
    agent_execution_permission.status = "DENIED"
    agent_execution_permission.user_feedback = "User feedback"
    next_step = AgentWorkflowStep()

    handler.session.query.return_value.filter.return_value.first.return_value = agent_execution_permission
    handler._handle_next_step = Mock()
    AgentWorkflowStep.fetch_next_step = Mock(return_value=next_step)

    # Act
    result = handler._handle_wait_for_permission(agent_execution, workflow_step)

    # Assert
    assert result == False
    handler._handle_next_step.assert_called_once_with(next_step)
    assert agent_execution.status == "RUNNING"
    assert agent_execution.permission_id == -1
