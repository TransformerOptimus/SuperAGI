from datetime import datetime

import pytest
from unittest.mock import Mock, patch

from superagi.jobs.agent_executor import AgentExecutor


class MockSession:
    def query(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return None

    def add(self, obj):
        return None

    def commit(self):
        return None

    def all(self):
        return []

    def order_by(self, *args, **kwargs):
        return self

class MockAgentConfiguration:
    def __init__(self, agent_id, key, value, updated_at=None):
        self._agent_id = agent_id
        self._key = key
        self._value = value
        self._updated_at = updated_at

    @property
    def updated_at(self):
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value):
        self._updated_at = value

    @property
    def agent_id(self):
        return self._agent_id

    @agent_id.setter
    def agent_id(self, value):
        self._agent_id = value

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

class MockResource:
    def __init__(self, id, agent_id, summary=None, update_at=None):
        self.id = id
        self._agent_id = agent_id
        self.summary = summary
        self.update_at = update_at

    @property
    def agent_id(self):
        return self._agent_id

    @agent_id.setter
    def agent_id(self, value):
        self._agent_id = value

    @property
    def updated_at(self):
        return self.update_at

    @updated_at.setter
    def updated_at(self, value):
        self.update_at = value

date_obj = datetime.strptime("2023-07-01 07:47:27.349297", '%Y-%m-%d %H:%M:%S.%f')


resources_mock_data = [
    MockResource(1, 1, "summary 1", date_obj),
    MockResource(2, 1, "summary 2", date_obj)
]

patched_generate_summary_of_texts = patch(
    "superagi.resource_manager.resource_manager.ResourceManager.generate_summary_of_texts", return_value="summary"
)

@patched_generate_summary_of_texts
def test_generate_resource_summary(generate_summary_of_texts):
    session = MockSession()
    openai_api_key = "mock_openai_key"
    agent_id = 1
    with patch('superagi.models.agent_config.AgentConfiguration', new=MockAgentConfiguration):
        with patch('superagi.models.resource.Resource', new=MockResource):
            with patch.object(MockSession, 'all', return_value=resources_mock_data):
                instance = AgentExecutor()
                result = instance.generate_resource_summary(agent_id=agent_id, session=session,
                                                            openai_api_key=openai_api_key)
                generate_summary_of_texts.assert_called_with(["summary 1", "summary 2"], openai_api_key)
                assert result == "summary"


@patched_generate_summary_of_texts
def test_generate_resource_summary_no_resources(generate_summary_of_texts):
    session = MockSession()
    openai_api_key = "mock_openai_key"
    agent_id = 1
    with patch('superagi.models.agent_config.AgentConfiguration', new=MockAgentConfiguration):
        with patch('superagi.models.resource.Resource', new=MockResource):
            with patch.object(MockSession, 'all', return_value=[]):
                instance = AgentExecutor()
                result = instance.generate_resource_summary(agent_id=agent_id, session=session,
                                                            openai_api_key=openai_api_key)
                generate_summary_of_texts.assert_not_called()
                assert result is None

@patched_generate_summary_of_texts
def test_generate_resource_summary_no_summary(generate_summary_of_texts):
    session = MockSession()
    openai_api_key = "mock_openai_key"
    agent_id = 1
    with patch('superagi.models.agent_config.AgentConfiguration', new=MockAgentConfiguration):
        with patch('superagi.models.resource.Resource', new=MockResource):
            with patch.object(MockSession, 'all', return_value=[MockResource(1, 1)]):
                instance = AgentExecutor()
                result = instance.generate_resource_summary(agent_id=agent_id, session=session,
                                                            openai_api_key=openai_api_key)
                generate_summary_of_texts.assert_not_called()
                assert result is None

@patched_generate_summary_of_texts
def test_generate_resource_summary_already_summarized(generate_summary_of_texts):
    session = MockSession()
    openai_api_key = "mock_openai_key"
    agent_id = 1
    last_resource = MockAgentConfiguration(agent_id=agent_id, key="last_resource_id", value="2023-07-01 07:47:27.349297")
    with patch('superagi.models.agent_config.AgentConfiguration', new=MockAgentConfiguration):
        with patch('superagi.models.resource.Resource', new=MockResource):
            with patch.object(MockSession, 'first', return_value=last_resource):
                with patch.object(MockSession, 'all', return_value=resources_mock_data):
                    instance = AgentExecutor()
                    result = instance.generate_resource_summary(agent_id=agent_id, session=session,
                                                                openai_api_key=openai_api_key)
                    generate_summary_of_texts.assert_not_called()
                    assert result is None
