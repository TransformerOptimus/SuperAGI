import pytest

from superagi.agent.output_parser import AgentGPTAction, AgentSchemaOutputParser

import pytest

def test_agent_schema_output_parser():
    parser = AgentSchemaOutputParser()

    # Test with valid json response
    response = '```{"tool": {"name": "Tool1", "args": {}}}```'
    parsed = parser.parse(response)
    assert isinstance(parsed, AgentGPTAction)
    assert parsed.name == 'Tool1'
    assert parsed.args == {}

    # Test with valid json but with boolean values
    response = "```{'tool': {'name': 'Tool1', 'args': 'arg1'}, 'status': True}```"
    parsed = parser.parse(response)
    assert isinstance(parsed, AgentGPTAction)
    assert parsed.name == 'Tool1'
    assert parsed.args == 'arg1'

    # Test with invalid json response
    response = "invalid response"
    with pytest.raises(Exception):
        parsed = parser.parse(response)

    # Test with empty json response
    response = ""
    with pytest.raises(Exception):
        parsed = parser.parse(response)



