from unittest.mock import Mock, patch

import requests

from superagi.models.agent_template import AgentTemplate
from superagi.models.workflows.agent_workflow import AgentWorkflow


def test_to_dict():
    agent_template = AgentTemplate(id=1, name='test', description='desc')
    result = agent_template.to_dict()
    assert result == {'id': 1, 'name': 'test', 'description': 'desc'}


def test_to_json():
    agent_template = AgentTemplate(id=1, name='test', description='desc')
    result = agent_template.to_json()
    assert result == '{"id": 1, "name": "test", "description": "desc"}'


def test_from_json():
    json_data = '{"id": 1, "name": "test", "description": "desc"}'
    agent_template = AgentTemplate.from_json(json_data)
    assert agent_template.id == 1
    assert agent_template.name == 'test'
    assert agent_template.description == 'desc'


def test_main_keys():
    keys = AgentTemplate.main_keys()
    assert isinstance(keys, list)
    assert 'goal' in keys
    assert 'instruction' in keys


@patch.object(requests, 'get')
def test_fetch_marketplace_list(mock_get):
    mock_get.return_value = Mock(status_code=200, json=lambda: [{'id': 1, 'name': 'test', 'description': 'desc'}])
    result = AgentTemplate.fetch_marketplace_list('test', 1)
    assert len(result) == 1
    assert result[0]['id'] == 1


@patch.object(requests, 'get')
def test_fetch_marketplace_detail(mock_get):
    mock_get.return_value = Mock(status_code=200, json=lambda: {'id': 1, 'name': 'test', 'description': 'desc'})
    result = AgentTemplate.fetch_marketplace_detail(1)
    assert result['id'] == 1
    assert result['name'] == 'test'
    assert result['description'] == 'desc'


def test_eval_agent_config():
    assert AgentTemplate.eval_agent_config('name', 'test') == 'test'
    assert AgentTemplate.eval_agent_config('project_id', '1') == 1
    assert AgentTemplate.eval_agent_config('goal', '["goal1", "goal2"]') == ["goal1", "goal2"]


@patch('superagi.models.agent_template.AgentTemplate.fetch_marketplace_detail')
@patch('sqlalchemy.orm.Session')
def test_clone_agent_template_from_marketplace(mock_session, mock_fetch_marketplace_detail):
    mock_fetch_marketplace_detail.return_value = {
        "id": 1,
        "name": "test",
        "description": "desc",
        "agent_workflow_name": "workflow1",
        "configs": {
            "config1": {"value": "value1"},
            "config2": {"value": "value2"}
        }
    }
    mock_session.query.return_value.filter.return_value.first.return_value = AgentWorkflow(id=1, name='workflow1')

    agent_template = AgentTemplate.clone_agent_template_from_marketplace(mock_session, 1, 1)

    assert isinstance(agent_template, AgentTemplate)
    assert agent_template.organisation_id == 1
    assert agent_template.name == 'test'
    assert agent_template.description == 'desc'