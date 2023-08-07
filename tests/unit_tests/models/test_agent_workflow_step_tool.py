from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from superagi.models.workflows.agent_workflow_step_tool import AgentWorkflowStepTool


@patch('sqlalchemy.orm.Session.query')
def test_find_by_id(mock_query):
    mock_query.return_value.filter.return_value.first.return_value = MagicMock(spec=AgentWorkflowStepTool)
    result = AgentWorkflowStepTool.find_by_id(Session(), 1)
    assert isinstance(result, AgentWorkflowStepTool)
@patch('sqlalchemy.orm.Session.add')
@patch('sqlalchemy.orm.Session.query')
def test_find_or_create_tool_new(mock_query, mock_add):
    mock_query.return_value.filter_by.return_value.first.return_value = None  # simulating tool doesn't exist
    session = MagicMock(spec=Session)
    session.query = mock_query
    tool = AgentWorkflowStepTool.find_or_create_tool(
        session=session,
        step_unique_id='test_step',
        tool_name='test_tool',
        input_instruction='test_input',
        output_instruction='test_output',
        history_enabled=False,
        completion_prompt='test_prompt'
    )
    assert tool.__class__ == AgentWorkflowStepTool

@patch('sqlalchemy.orm.Session.query')
def test_find_or_create_tool_exists(mock_query):
    mock_tool = MagicMock(spec=AgentWorkflowStepTool)
    mock_query.return_value.filter_by.return_value.first.return_value = mock_tool  # simulating tool already exists
    session = MagicMock(spec=Session)
    session.query = mock_query
    tool = AgentWorkflowStepTool.find_or_create_tool(
        session=session,
        step_unique_id='test_step',
        tool_name='test_tool',
        input_instruction='test_input',
        output_instruction='test_output',
        history_enabled=False,
        completion_prompt='test_prompt'
    )
    assert tool == mock_tool
