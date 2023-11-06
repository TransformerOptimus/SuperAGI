import pytest
from unittest.mock import patch, mock_open

from superagi.agent.agent_prompt_template import AgentPromptTemplate
from superagi.helper.prompt_reader import PromptReader


@patch("builtins.open", new_callable=mock_open, read_data="test_prompt")
def test_get_super_agi_single_prompt(mock_file):
    expected_result = {"prompt": "test_prompt", "variables": ["goals", "instructions", "constraints", "tools"]}
    result = AgentPromptTemplate.get_super_agi_single_prompt()
    assert result == expected_result

@patch("builtins.open", new_callable=mock_open, read_data="test_prompt")
def test_start_task_based(mock_file):
    expected_result = {"prompt": "test_prompt", "variables": ["goals", "instructions"]}
    result = AgentPromptTemplate.start_task_based()
    assert result == expected_result

@patch("builtins.open", new_callable=mock_open, read_data="test_prompt")
def test_analyse_task(mock_file):
    expected_result = {"prompt": "test_prompt",
                       "variables": ["goals", "instructions", "tools", "current_task"]}
    result = AgentPromptTemplate.analyse_task()
    assert result == expected_result

@patch("builtins.open", new_callable=mock_open, read_data="test_prompt")
def test_create_tasks(mock_file):
    expected_result = {"prompt": "test_prompt", "variables": ["goals", "instructions", "last_task", "last_task_result", "pending_tasks"]}
    result = AgentPromptTemplate.create_tasks()
    assert result == expected_result

@patch("builtins.open", new_callable=mock_open, read_data="test_prompt")
def test_prioritize_tasks(mock_file):
    expected_result = {"prompt": "test_prompt", "variables": ["goals", "instructions", "last_task", "last_task_result", "pending_tasks"]}
    result = AgentPromptTemplate.prioritize_tasks()
    assert result == expected_result
