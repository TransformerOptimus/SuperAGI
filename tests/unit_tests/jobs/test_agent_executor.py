import pytest
from unittest.mock import MagicMock

from superagi.jobs.agent_executor import AgentExecutor
from superagi.models.tool import Tool
from superagi.tools.file.write_file import WriteFileTool


def test_validate_filename():
    # Test when filename ends with ".py"
    assert AgentExecutor.validate_filename("tool.py") == "tool"

    # Test when filename doesn't end with ".py"
    assert AgentExecutor.validate_filename("tool") == "tool"


def test_create_object():
    # Setup mock objects
    tool = Tool()
    tool.file_name = "file_toolkit.py"
    tool.folder_name = "file"
    tool.class_name = "WriteFileTool"
    tool.toolkit_id = 1

    session = MagicMock()

    # Test creating an object
    obj = AgentExecutor.create_object(tool, session)

    # Assertions
    assert isinstance(obj, WriteFileTool)
    assert obj.toolkit_config.session == session
    assert obj.toolkit_config.toolkit_id == tool.toolkit_id
