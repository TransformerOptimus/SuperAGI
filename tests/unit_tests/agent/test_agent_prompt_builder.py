from unittest.mock import Mock
from unittest.mock import patch

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.tools.base_tool import BaseTool


def test_add_list_items_to_string():
    items = ['item1', 'item2', 'item3']
    result = AgentPromptBuilder.add_list_items_to_string(items)
    assert result == '1. item1\n2. item2\n3. item3\n'


def test_clean_prompt():
    prompt = '   some   text  with    extra spaces     '
    result = AgentPromptBuilder.clean_prompt(prompt)
    assert result == 'some text with extra spaces'


@patch('superagi.agent.agent_prompt_builder.AgentPromptBuilder.add_list_items_to_string')
@patch('superagi.agent.agent_prompt_builder.AgentPromptBuilder.add_tools_to_prompt')
def test_replace_main_variables(mock_add_tools_to_prompt, mock_add_list_items_to_string):
    super_agi_prompt = "{goals} {instructions} {task_instructions} {constraints} {tools}"
    goals = ['goal1', 'goal2']
    instructions = ['instruction1']
    constraints = ['constraint1']
    tools = [Mock(spec=BaseTool)]

    # Mocking
    mock_add_list_items_to_string.side_effect = lambda x: ', '.join(x)
    mock_add_tools_to_prompt.return_value = 'tools_str'

    result = AgentPromptBuilder.replace_main_variables(super_agi_prompt, goals, instructions, constraints, tools)

    assert 'goal1, goal2 INSTRUCTION' in result
    assert 'instruction1' in result
    assert 'constraint1' in result


@patch('superagi.agent.agent_prompt_builder.TokenCounter.count_message_tokens')
def test_replace_task_based_variables(mock_count_message_tokens):
    super_agi_prompt = "{current_task} {last_task} {last_task_result} {pending_tasks} {completed_tasks} {task_history}"
    current_task = "task1"
    last_task = "task2"
    last_task_result = "result1"
    pending_tasks = ["task3", "task4"]
    completed_tasks = [{'task': 'task1', 'response': 'response1'}, {'task': 'task2', 'response': 'response2'}]
    token_limit = 2000

    # Mocking
    mock_count_message_tokens.return_value = 50

    result = AgentPromptBuilder.replace_task_based_variables(super_agi_prompt, current_task, last_task, last_task_result,
                                                             pending_tasks, completed_tasks, token_limit)

    expected_result = f"{current_task} {last_task} {last_task_result} {str(pending_tasks)} {str([x['task'] for x in completed_tasks])} \nTask: {completed_tasks[-1]['task']}\nResult: {completed_tasks[-1]['response']}\nTask: {completed_tasks[-2]['task']}\nResult: {completed_tasks[-2]['response']}\n"

    assert result == expected_result


@patch('superagi.agent.agent_prompt_builder.TokenCounter.count_message_tokens')
def test_replace_task_based_variables(mock_count_message_tokens):
    super_agi_prompt = "{current_task} {last_task} {last_task_result} {pending_tasks} {completed_tasks} {task_history}"
    current_task = "task1"
    last_task = "task2"
    last_task_result = "result1"
    pending_tasks = ["task3", "task4"]
    completed_tasks = [{'task': 'task1', 'response': 'response1'}, {'task': 'task2', 'response': 'response2'}]
    token_limit = 2000

    # Mocking
    mock_count_message_tokens.return_value = 50

    result = AgentPromptBuilder.replace_task_based_variables(super_agi_prompt, current_task, last_task, last_task_result,
                                                             pending_tasks, completed_tasks, token_limit)

    # expected_result = f"{current_task} {last_task} {last_task_result} {str(pending_tasks)} {str([x['task'] for x in reversed(completed_tasks)])} \nTask: {completed_tasks[-1]['task']}\nResult: {completed_tasks[-1]['response']}\nTask: {completed_tasks[-2]['task']}\nResult: {completed_tasks[-2]['response']}\n"

    assert "task1" in result
    assert "task2" in result
    assert "result1" in result
    assert "task3" in result
    assert "task3" in result
    assert "response1" in result
    assert "response2" in result