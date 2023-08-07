import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch
from superagi.tools.file.read_file import ReadFileTool  

from superagi.models.agent_execution import AgentExecution
from superagi.tools.file.read_file import ReadFileTool
from superagi.models.agent import Agent

@pytest.fixture
def mock_os_path_exists():
    with patch("os.path.exists") as mock_exists:
        yield mock_exists

@pytest.fixture
def mock_os_makedirs():
    with patch("os.makedirs") as mock_makedirs:
        yield mock_makedirs

@pytest.fixture
def mock_get_config():
    with patch("superagi.config.config.get_config") as mock_get_config:
        yield mock_get_config


@pytest.fixture
def read_file_tool():
    read_file_tool = ReadFileTool()
    read_file_tool.agent_id = 1  # Set a dummy agent ID for testing.

@pytest.fixture
def mock_s3_helper():
    with patch("superagi.helper.s3_helper.S3Helper") as mock_s3_helper:
        yield mock_s3_helper

@pytest.fixture
def mock_partition():
    with patch("unstructured.partition.auto.partition") as mock_partition:
        yield mock_partition

@pytest.fixture
def mock_get_agent_from_id():
    with patch("superagi.models.agent.Agent.get_agent_from_id") as mock_get_agent:
        yield mock_get_agent

@pytest.fixture
def mock_get_agent_execution_from_id():
    with patch("superagi.models.agent_execution.AgentExecution.get_agent_execution_from_id") as mock_execution:
        yield mock_execution
@pytest.fixture
def mock_resource_helper():
    with patch("superagi.helper.resource_helper.ResourceHelper.get_agent_read_resource_path") as mock_resource_helper:
        yield mock_resource_helper

def test_read_file_tool(mock_os_path_exists, mock_os_makedirs, mock_get_config, mock_s3_helper, mock_partition,
                        mock_get_agent_from_id, mock_get_agent_execution_from_id, mock_resource_helper):
    mock_os_path_exists.return_value = True
    mock_partition.return_value = ["This is a file.", "This is the second line."]
    mock_get_config.return_value = "FILE"
    mock_get_agent_from_id.return_value = MagicMock()
    mock_get_agent_execution_from_id.return_value = MagicMock()

    tool = ReadFileTool()

    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as tmp:
        tmp.write("This is a file.\nThis is the second line.")
        tmp.seek(0)  # Reset file pointer to the beginning
        tmp.close()  # Explicitly close the file

        mock_resource_helper.return_value = tmp.name

        try:
            result = tool._execute(tmp.name)
            assert isinstance(result, str)
            assert "This is a file." in result
            assert "This is the second line." in result
        finally:
            os.remove(tmp.name)  # Ensure the temporary file is deleted
  
def test_read_file_tool_s3(mock_os_path_exists, mock_os_makedirs, mock_get_config, mock_s3_helper, mock_partition,
                           mock_get_agent_from_id, mock_get_agent_execution_from_id, mock_resource_helper):
    mock_os_path_exists.return_value = True
    mock_get_config.return_value = "S3"  # ensure this function returns "S3"
    mock_get_agent_from_id.return_value = MagicMock()
    mock_get_agent_execution_from_id.return_value = MagicMock()

    tool = ReadFileTool()

    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as tmp:
        tmp.write("This is a file.\nThis is the second line.")
        tmp.seek(0)  # Reset file pointer to the beginning
        tmp.close()  # Explicitly close the file

        mock_resource_helper.return_value = tmp.name
        mock_s3_helper.return_value.read_from_s3.return_value = open(tmp.name, 'r').read()

        try:
            result = tool._execute(tmp.name)
            assert isinstance(result, str)
            assert "This is a file." in result
            assert "This is the second line." in result
        finally:
            os.remove(tmp.name)  # Ensure the temporary file is deleted

    
def test_read_file_tool_not_found(mock_os_path_exists, mock_os_makedirs, mock_get_config, mock_s3_helper, mock_partition,
                                  mock_get_agent_from_id, mock_get_agent_execution_from_id, mock_resource_helper):
    mock_os_path_exists.return_value = False
    mock_get_agent_from_id.return_value = MagicMock()
    mock_get_agent_execution_from_id.return_value = MagicMock()

    tool = ReadFileTool()

    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as tmp:
        tmp.write("This is a file.\nThis is the second line.")
        tmp.seek(0)  # Reset file pointer to the beginning
        tmp.close()  # Explicitly close the file

        try:
            with pytest.raises(FileNotFoundError):
                tool._execute(tmp.name)
        finally:
            os.remove(tmp.name)  # Ensure the temporary file is deleted


