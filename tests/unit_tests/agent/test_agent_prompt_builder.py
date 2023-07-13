from unittest.mock import MagicMock

import pytest
from unittest.mock import patch, MagicMock
import json
from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.helper.prompt_reader import PromptReader
from superagi.tools.base_tool import BaseTool
from superagi.tools.email.send_email import SendEmailTool


def test_add_list_items_to_string():
    items = ['apple', 'banana', 'cherry']
    result = AgentPromptBuilder.add_list_items_to_string(items)
    expected_result = "1. apple\n2. banana\n3. cherry\n"
    assert result == expected_result


def test_clean_prompt():
    prompt = "  This is a   prompt with    unnecessary spaces   .  "
    result = AgentPromptBuilder.clean_prompt(prompt)
    expected_result = "This is a prompt with unnecessary spaces ."
    assert result == expected_result


class MockTool(BaseTool):
    name: str = "Mock Tool"
    description: str = "This is a mock tool."

    def _execute(self):
        pass


def test_replace_main_variables():
    goals = ["goal1", "goal2"]
    instructions = ["instruction1", "instruction2"]
    constraints = ["constraint1", "constraint2"]

    mock_tool = MockTool()

    tool1 = mock_tool
    tool2 = mock_tool
    tools = [tool1, tool2]

    super_agi_prompt = "Goals:\n{goals}\nInstructions:\n{instructions}\nConstraints:\n{constraints}\nTools:\n{tools}"

    result = AgentPromptBuilder.replace_main_variables(super_agi_prompt, goals, instructions, constraints, tools)

    assert "instruction1" in result
    assert "instruction2" in result
    assert "constraint1" in result
    assert "constraint2" in result
    assert "Mock Tool" in result


def test__generate_command_string():
    tool = SendEmailTool(name="Mock Tool", description="This is a mock tool.")
    result = AgentPromptBuilder._generate_command_string(tool)
    expected_result = "\"Mock Tool\": This is a mock tool."
    assert (expected_result in result)


def test_get_super_agi_single_prompt():
    # Arrange
    prompt_mock = "Mocked prompt with {response_format}"
    with patch('superagi.helper.prompt_reader.PromptReader.read_agent_prompt', return_value=prompt_mock):
        # Act
        result = AgentPromptBuilder.get_super_agi_single_prompt()

        # Assert
        expected_response_format = {
            "thoughts": {
                "text": "thought",
                "reasoning": "short reasoning",
                "plan": "- short bulleted\n- list that conveys\n- long-term plan",
                "criticism": "constructive self-criticism",
                "speak": "thoughts summary to say to user",
            },
            "tool": {"name": "tool name/task name",
                     "args": {"arg name": "arg value(escape in case of string)"}}
        }
        formatted_response_format = json.dumps(expected_response_format, indent=4)

        expected_prompt = "Mocked prompt with " + formatted_response_format
        expected_result = {"prompt": expected_prompt, "variables": ["goals", "instructions", "constraints", "tools"]}

        assert result == expected_result


def test_analyse_task():
    # Arrange
    mock_prompt = "Mocked prompt with {constraints}"
    mock_read_agent_prompt = MagicMock(return_value=mock_prompt)
    with patch.object(PromptReader, 'read_agent_prompt', new=mock_read_agent_prompt):
        constraints = ['Exclusively use the tools listed in double quotes e.g. "tool name"']

        # Act
        result = AgentPromptBuilder.analyse_task()

        # Assert
        expected_prompt = AgentPromptBuilder.clean_prompt(mock_prompt).replace(
            "{constraints}", AgentPromptBuilder.add_list_items_to_string(constraints))

        assert result == {"prompt": expected_prompt, "variables": ["goals", "instructions", "tools", "current_task"]}


@pytest.fixture
def base_tool():
    return MockTool(name="base_tool", description="description", args_schema=None, permission_required=True)


@pytest.mark.parametrize("completed_tasks, expected_output", [
    ([], ""),
    ([{'task': 'task1', 'response': 'response1'}], "Task: task1\nResult: response1\n")
])
def test_replace_task_based_variables(base_tool, completed_tasks, expected_output):
    current_task = "current_task"
    last_task = "last_task"
    last_task_result = "last_task_result"
    pending_tasks = ["task1", "task2"]
    token_limit = 1000
    super_agi_prompt = "{current_task} {last_task} {last_task_result} {pending_tasks} {completed_tasks} {task_history}"
    replaced_prompt = AgentPromptBuilder.replace_task_based_variables(
        super_agi_prompt, current_task, last_task, last_task_result, pending_tasks, completed_tasks, token_limit)

    assert "{current_task}" not in replaced_prompt
    assert "{last_task}" not in replaced_prompt
    assert "{last_task_result}" not in replaced_prompt
    assert "{pending_tasks}" not in replaced_prompt
    assert "{completed_tasks}" not in replaced_prompt
    assert "{task_history}" not in replaced_prompt

    assert current_task in replaced_prompt
    assert last_task in replaced_prompt
    assert last_task_result in replaced_prompt
    assert str(pending_tasks) in replaced_prompt
    assert str([task['task'] for task in completed_tasks]) in replaced_prompt
    assert expected_output in replaced_prompt


def test_create_tasks():
    super_agi_prompt = AgentPromptBuilder.create_tasks()
    assert isinstance(super_agi_prompt, dict)
    assert "prompt" in super_agi_prompt
    assert "variables" in super_agi_prompt
    assert super_agi_prompt["variables"] == ["goals", "instructions", "last_task", "last_task_result", "pending_tasks"]

    # Now we validate the prompt
    prompt = super_agi_prompt["prompt"]
    assert "{goals}" in prompt
    assert "{task_instructions}" in prompt
    assert "{completed_tasks}" in prompt

def test_start_task_based():
    super_agi_prompt = AgentPromptBuilder.start_task_based()
    assert isinstance(super_agi_prompt, dict)
    assert "prompt" in super_agi_prompt
    assert "variables" in super_agi_prompt
    assert super_agi_prompt["variables"] == ["goals", "instructions"]

    # Now we validate the prompt
    prompt = super_agi_prompt["prompt"]
    assert "{goals}" in prompt
    assert "{instructions}" not in prompt

def test_prioritize_tasks():
    super_agi_prompt = AgentPromptBuilder.prioritize_tasks()
    assert isinstance(super_agi_prompt, dict)
    assert "prompt" in super_agi_prompt
    assert "variables" in super_agi_prompt
    assert super_agi_prompt["variables"] == ["goals", "instructions", "last_task", "last_task_result", "pending_tasks"]

    # Now we validate the prompt
    prompt = super_agi_prompt["prompt"]
    assert "{goals}" in prompt
    assert "{pending_tasks}" in prompt