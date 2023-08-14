import pytest
from unittest.mock import MagicMock, patch, Mock
from sqlalchemy.orm import Session
import json
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep


@patch('sqlalchemy.orm.Session.query')
def test_find_by_id(mock_query):
    mock_query.return_value.filter.return_value.first.return_value = MagicMock(spec=AgentWorkflowStep)
    result = AgentWorkflowStep.find_by_id(Session(), 1)
    assert isinstance(result, AgentWorkflowStep)

@patch('sqlalchemy.orm.Session.query')
def test_find_by_unique_id(mock_query):
    mock_query.return_value.filter.return_value.first.return_value = MagicMock(spec=AgentWorkflowStep)
    result = AgentWorkflowStep.find_by_unique_id(Session(), '1')
    assert isinstance(result, AgentWorkflowStep)

def test_from_json():
    data = {
        'id': 1,
        'agent_workflow_id': 1,
        'unique_id': '1',
        'step_type': 'TRIGGER',
        'action_type': 'TOOL',
        'action_reference_id': 1,
        'next_steps': []
    }
    result = AgentWorkflowStep.from_json(json.dumps(data))
    assert isinstance(result, AgentWorkflowStep)

def test_to_dict():
    step = AgentWorkflowStep(
        id=1,
        agent_workflow_id=1,
        unique_id='1',
        step_type='TRIGGER',
        action_type='TOOL',
        action_reference_id=1,
        next_steps=[]
    )
    result = step.to_dict()
    assert isinstance(result, dict)
    assert result['id'] == 1
    assert result['agent_workflow_id'] == 1
    assert result['unique_id'] == '1'
    assert result['step_type'] == 'TRIGGER'
    assert result['action_type'] == 'TOOL'
    assert result['action_reference_id'] == 1
    assert result['next_steps'] == []


@patch('sqlalchemy.orm.Session.add')
@patch('sqlalchemy.orm.Session.commit')
@patch('sqlalchemy.orm.Session.query')
@patch('superagi.models.workflows.agent_workflow_step.AgentWorkflowStepTool.find_or_create_tool')
def test_find_or_create_tool_workflow_step(mock_find_or_create_tool, mock_query, mock_commit, mock_add):
    mock_find_or_create_tool.return_value = MagicMock(id=2)
    mock_query.return_value.filter.return_value.first.return_value = None  # to simulate workflow_step not exists yet
    session = MagicMock(spec=Session)
    session.query = mock_query
    result = AgentWorkflowStep.find_or_create_tool_workflow_step(
        session=session,
        agent_workflow_id=1,
        unique_id='1',
        tool_name='test_tool',
        input_instruction='test_instruction'
    )
    assert isinstance(result, AgentWorkflowStep)
    assert result.agent_workflow_id == 1
    assert result.unique_id == '1'
    assert result.action_type == 'TOOL'
    assert result.action_reference_id == 2
    assert result.next_steps == []

@patch('sqlalchemy.orm.Session.commit')
@patch('sqlalchemy.orm.Session.query')
@patch('superagi.models.workflows.agent_workflow_step.AgentWorkflowStepTool.find_or_create_tool')
def test_find_or_create_tool_workflow_step_exists(mock_find_or_create_tool, mock_query, mock_commit):
    existing_workflow_step = MagicMock(spec=AgentWorkflowStep)
    mock_find_or_create_tool.return_value = MagicMock(id=2)
    mock_query.return_value.filter.return_value.first.return_value = existing_workflow_step
    session = MagicMock(spec=Session)
    session.query = mock_query
    result = AgentWorkflowStep.find_or_create_tool_workflow_step(
        session=session,
        agent_workflow_id=1,
        unique_id='1',
        tool_name='test_tool',
        input_instruction='test_instruction'
    )
    assert result == existing_workflow_step


@patch('sqlalchemy.orm.Session.commit')
@patch('sqlalchemy.orm.Session.query')
@patch('superagi.models.workflows.iteration_workflow.IterationWorkflow.find_workflow_by_name')
def test_find_or_create_iteration_workflow_step_exists(mock_find_workflow_by_name, mock_query, mock_commit):
    existing_workflow_step = MagicMock(spec=AgentWorkflowStep)
    mock_find_workflow_by_name.return_value = MagicMock(id=2)
    mock_query.return_value.filter.return_value.first.return_value = existing_workflow_step
    session = MagicMock(spec=Session)
    session.query = mock_query
    result = AgentWorkflowStep.find_or_create_iteration_workflow_step(
        session=session,
        agent_workflow_id=1,
        unique_id='1',
        iteration_workflow_name='test_iteration_workflow',
        step_type='NORMAL'
    )
    assert result == existing_workflow_step


@patch('sqlalchemy.orm.Session.commit')
@patch('sqlalchemy.orm.Session.query')
@patch('superagi.models.workflows.agent_workflow_step.AgentWorkflowStep.find_by_id')
def test_add_next_workflow_step(mock_find_by_id, mock_query, mock_commit):
    next_workflow_step = MagicMock(spec=AgentWorkflowStep, unique_id='2')
    mock_find_by_id.return_value = next_workflow_step
    current_step = MagicMock(spec=AgentWorkflowStep, next_steps=[])
    mock_query.return_value.filter.return_value.first.return_value = current_step
    session = MagicMock(spec=Session)
    session.query = mock_query
    result = AgentWorkflowStep.add_next_workflow_step(
        session=session,
        current_agent_step_id=1,
        next_step_id=2,
        step_response='test_response'
    )
    assert result == current_step
    assert len(result.next_steps) == 1
    assert result.next_steps[0]['step_response'] == 'test_response'
    assert result.next_steps[0]['step_id'] == '2'

@patch('sqlalchemy.orm.Session.commit')
@patch('sqlalchemy.orm.Session.query')
@patch('superagi.models.workflows.agent_workflow_step.AgentWorkflowStep.find_by_id')
def test_add_next_workflow_step_existing(mock_find_by_id, mock_query, mock_commit):
    next_workflow_step = MagicMock(spec=AgentWorkflowStep, unique_id='2')
    mock_find_by_id.return_value = next_workflow_step
    current_step = MagicMock(spec=AgentWorkflowStep, next_steps=[{"step_response": 'previous_response', "step_id": '2'}])
    mock_query.return_value.filter.return_value.first.return_value = current_step
    session = MagicMock(spec=Session)
    session.query = mock_query
    result = AgentWorkflowStep.add_next_workflow_step(
        session=session,
        current_agent_step_id=1,
        next_step_id=2,
        step_response='test_response'
    )
    assert result == current_step
    assert len(result.next_steps) == 1
    assert result.next_steps[0]['step_response'] == 'test_response'
    assert result.next_steps[0]['step_id'] == '2'


@patch('superagi.models.workflows.agent_workflow_step.AgentWorkflowStep.find_by_id')
@patch('superagi.models.workflows.agent_workflow_step.AgentWorkflowStep.find_by_unique_id')
def test_fetch_default_next_step(mock_find_by_unique_id, mock_find_by_id):
    current_step = MagicMock(spec=AgentWorkflowStep, next_steps=[{"step_response": 'default', "step_id": '2'}])
    next_step = MagicMock(spec=AgentWorkflowStep, unique_id='2')
    mock_find_by_id.return_value = current_step
    mock_find_by_unique_id.return_value = next_step
    session = MagicMock(spec=Session)
    result = AgentWorkflowStep.fetch_default_next_step(
        session=session,
        current_agent_step_id=1,
    )
    assert result == next_step

@patch('superagi.models.workflows.agent_workflow_step.AgentWorkflowStep.find_by_id')
def test_fetch_default_next_step_none(mock_find_by_id):
    current_step = MagicMock(spec=AgentWorkflowStep, next_steps=[{"step_response": 'non-default', "step_id": '2'}])
    mock_find_by_id.return_value = current_step
    session = MagicMock(spec=Session)
    result = AgentWorkflowStep.fetch_default_next_step(
        session=session,
        current_agent_step_id=1,
    )
    assert result is None