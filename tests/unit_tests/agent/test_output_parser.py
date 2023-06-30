import pytest
from superagi.agent.output_parser import AgentOutputParser, AgentGPTAction, AgentTasks


def test_parse():
    parser = AgentOutputParser()

    # test with valid input
    valid_text = '{"thoughts": {"text": "some thought", "reasoning": "some reasoning", "plan": "some plan", "criticism": "some criticism"}, "tool": {"name": "some tool", "args": {"arg1": "value1"}}}'
    output = parser.parse(valid_text)
    assert isinstance(output, AgentGPTAction)
    assert output.name == "some tool"
    assert output.args == {"arg1": "value1"}

    # test with invalid json
    invalid_json = '{"this is not valid json'
    with pytest.raises(ValueError):
        parser.parse(invalid_json)


def test_parse_tasks():
    parser = AgentOutputParser()

    # test with valid input
    valid_text = '{"tasks": [{"task1": "value1"}, {"task2": "value2"}]}'
    output = parser.parse_tasks(valid_text)
    assert isinstance(output, AgentTasks)
    assert output.tasks == [{"task1": "value1"}, {"task2": "value2"}]
    assert output.error == ""

    # test with incomplete tool args
    invalid_tasks = '{"tasks": []}'
    output = parser.parse_tasks(invalid_tasks)
    assert isinstance(output, AgentTasks)
    assert output.tasks == []
    assert output.error == ""

    # test with invalid json
    invalid_json = '{"this is not valid json'
    output = parser.parse_tasks(invalid_json)
    assert isinstance(output, AgentTasks)
    assert "Could not parse invalid json" in output.error
