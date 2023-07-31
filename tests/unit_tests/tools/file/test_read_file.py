import pytest
from unittest.mock import MagicMock, patch
from superagi.tools.file.read_file import ReadFileTool  # replace with the actual import path for your class

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

def test_read_file_tool_txt(mock_os_path_exists, mock_os_makedirs, mock_get_config, mock_s3_helper, mock_partition,
                            mock_get_agent_from_id, mock_get_agent_execution_from_id):
    mock_os_path_exists.return_value = True
    mock_partition.return_value = ["This is a text file.", "This is the second line."]
    mock_get_config.return_value = "FILE"
    mock_get_agent_from_id.return_value = MagicMock()
    mock_get_agent_execution_from_id.return_value = MagicMock()

    tool = ReadFileTool()
    file_name = "sample.txt"
    result = tool._execute(file_name)

    assert isinstance(result, str)
    

def test_read_file_tool_s3(mock_os_path_exists, mock_os_makedirs, mock_get_config, mock_s3_helper, mock_partition,
                            mock_get_agent_from_id, mock_get_agent_execution_from_id):
    mock_os_path_exists.return_value = True
    mock_get_config.return_value = "S3"  # ensure this function returns "S3"
    mock_s3_helper.return_value.read_from_s3.return_value = "sample.txt"  # adjust this to match actual output
    mock_get_agent_from_id.return_value = MagicMock()
    mock_get_agent_execution_from_id.return_value = MagicMock()

    tool = ReadFileTool()
    file_name = "sample.txt"
    result = tool._execute(file_name)

    assert isinstance(result, str)
    
                         
def test_read_file_tool_not_found(mock_os_path_exists, mock_os_makedirs, mock_get_config, mock_s3_helper, mock_partition,
                            mock_get_agent_from_id, mock_get_agent_execution_from_id):
    mock_os_path_exists.return_value = False
    mock_get_agent_from_id.return_value = MagicMock()
    mock_get_agent_execution_from_id.return_value = MagicMock()

    tool = ReadFileTool()
    file_name = "sample.txt"
    with pytest.raises(FileNotFoundError):
        tool._execute(file_name)




