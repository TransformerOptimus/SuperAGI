import pytest
from unittest.mock import MagicMock, Mock
from superagi.agent.output_parser import AgentOutputParser
from superagi.agent.super_agi import SuperAgi
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool
from superagi.vector_store.base import VectorStore


class MockTool(BaseTool):
    def __init__(self, name, permission_required=False):
        super().__init__(name=name, permission_required=permission_required, description="Mock tool")

    def _execute(self, *args, **kwargs):
        pass


class MockSession:
    def add(self, instance):
        pass

    def commit(self):
        pass

@pytest.fixture
def super_agi():
    ai_name = "test_ai"
    ai_role = "test_role"
    llm = Mock(spec=BaseLlm)
    memory = Mock(spec=VectorStore)
    tools = [MockTool(name="NotRestrictedTool", permission_required=False),
             MockTool(name="RestrictedTool", permission_required=True)]
    agent_config = {"permission_type": "RESTRICTED", "agent_execution_id": 1, "agent_id": 2}
    output_parser = AgentOutputParser()

    super_agi = SuperAgi(ai_name, ai_role, llm, memory, tools, agent_config, output_parser)
    return super_agi


def test_check_permission_in_restricted_mode_not_required(super_agi):
    assistant_reply = "Test reply"

    super_agi.output_parser.parse = MagicMock(
        return_value=MockTool(name="NotRestrictedTool", permission_required=False))
    result, output = super_agi.check_permission_in_restricted_mode(assistant_reply,MockSession())
    assert not result
    assert output is None


def test_check_permission_in_restricted_mode_permission_required(super_agi, monkeypatch):
    assistant_reply = "Test reply"

    mock_tool_requiring_permission = MockTool(name="RestrictedTool", permission_required=True)
    mock_tool_requiring_permission.permission_required = True
    super_agi.output_parser.parse = MagicMock(
        return_value=mock_tool_requiring_permission)


    # monkeypatch.setattr("superagi.agent.super_agi.session", MockSession())

    result, output = super_agi.check_permission_in_restricted_mode(assistant_reply,MockSession())
    assert result
    assert output["result"] == "WAITING_FOR_PERMISSION"
