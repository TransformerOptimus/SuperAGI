import pytest

from superagi.agent.output_parser import AgentGPTAction, AgentSchemaOutputParser


def test_parse():
    parser = AgentSchemaOutputParser()

    # test with valid input
    valid_text = '{"thoughts": {"text": "some thought", "reasoning": "some reasoning", "plan": "some plan", "criticism": "some criticism"}, "tool": {"name": "some tool", "args": {"arg1": "value1"}}}'
    output = parser.parse(valid_text)
    assert isinstance(output, AgentGPTAction)
    assert output.name == "some tool"
    assert output.args == {"arg1": "value1"}

