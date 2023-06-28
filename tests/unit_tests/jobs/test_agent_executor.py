import pytest
from unittest.mock import MagicMock

from superagi.jobs.agent_executor import AgentExecutor


def test_validate_filename():
    # Test when filename ends with ".py"
    assert AgentExecutor.validate_filename("tool.py") == "tool"

    # Test when filename doesn't end with ".py"
    assert AgentExecutor.validate_filename("tool") == "tool"