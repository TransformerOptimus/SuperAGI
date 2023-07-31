# import pytest
# from unittest.mock import patch, mock_open, MagicMock

# from superagi.models.agent_execution import AgentExecution
# from superagi.tools.file.read_file import ReadFileTool
# from superagi.models.agent import Agent


# @pytest.fixture
# def read_file_tool():
#     read_file_tool = ReadFileTool()
#     read_file_tool.agent_id = 1  # Set a dummy agent ID for testing.

#     yield read_file_tool


# def test_read_file_success(read_file_tool):
#     # Mock the open function, and make it return a file object that has 'Hello, World!' as its contents.
#     mock_file = mock_open(read_data='Hello, World!')
#     with patch('builtins.open', mock_file), \
#             patch('os.path.exists', return_value=True), \
#             patch('os.makedirs', return_value=True), \
#             patch('superagi.helper.resource_helper.ResourceHelper.get_root_input_dir',
#                   return_value="/input_dir/{agent_id}/"), \
#             patch('superagi.helper.resource_helper.ResourceHelper.get_root_output_dir',
#                   return_value="/output_dir/{agent_id}/"), \
#             patch('superagi.models.agent.Agent.get_agent_from_id', return_value=Agent(id=1, name='TestAgent')), \
#             patch('superagi.models.agent_execution.AgentExecution.get_agent_execution_from_id',
#                   return_value=
#                   AgentExecution(id=1, name='TestExecution')):
#         read_file_tool.toolkit_config.session = MagicMock()
#         file_content = read_file_tool._execute('file.txt')

#     expected_content = 'Hello, World!\n File file.txt read successfully.'
#     assert file_content == expected_content


# def test_read_file_file_not_found(read_file_tool):
#     with patch('os.path.exists', return_value=False), \
#             patch('superagi.helper.resource_helper.ResourceHelper.get_root_input_dir',
#                   return_value="/input_dir/{agent_id}/"), \
#             patch('superagi.helper.resource_helper.ResourceHelper.get_root_output_dir',
#                   return_value="/output_dir/{agent_id}/"), \
#             patch('superagi.models.agent.Agent.get_agent_from_id', return_value=Agent(id=1, name='TestAgent')), \
#             patch('superagi.models.agent_execution.AgentExecution.get_agent_execution_from_id',
#                   return_value=AgentExecution(id=1, name='TestExecution')):
#         read_file_tool.toolkit_config.session = MagicMock()
#         with pytest.raises(FileNotFoundError):
#             read_file_tool._execute('file.txt')

# import pytest
# from unittest.mock import patch, mock_open, MagicMock
# from superagi.models.agent_execution import AgentExecution
# from superagi.tools.file.read_file import ReadFileTool
# from superagi.models.agent import Agent

# @pytest.fixture
# @pytest.fixture
# def read_file_tool():
#     read_file_tool = ReadFileTool()
#     read_file_tool.agent_id = 1  # Set a dummy agent ID for testing.
#     yield read_file_tool

# def test_read_file_success_pdf(read_file_tool):
#     # Path to a test PDF file in your test suite.
#     pdf_file_path = "/home/adarsh/Downloads/pdf_file.pdf"  
#     # Mock the open function, and make it return a file object that has the contents of your PDF file.
#     mock_file = mock_open(read_data=b"Expected content of PDF.")
#     with patch('builtins.open', mock_file), \
#             patch('os.path.exists', return_value=True), \
#             patch('os.makedirs', return_value=True), \
#             patch('superagi.models.agent.Agent.get_agent_from_id', return_value=Agent(id=1)), \
#             patch('superagi.models.agent_execution.AgentExecution.get_agent_execution_from_id',
#                   return_value=AgentExecution(id=1)):
#         read_file_tool.toolkit_config.session = MagicMock()
#         file_content = read_file_tool._execute(pdf_file_path)
#     assert "LATEX" in file_content  # change "expected content" to the content you expect from PDF

# def test_read_file_success_csv(read_file_tool):
#     # Path to a test CSV file in your test suite.
#     csv_file_path = "home/adarsh/Downloads/SampleData.csv"  
#     # Mock the open function, and make it return a file object that has the contents of your CSV file.
#     mock_file = mock_open(read_data="Expected content of CSV.")
#     with patch('builtins.open', mock_file), \
#             patch('os.path.exists', return_value=True), \
#             patch('os.makedirs', return_value=True), \
#             patch('superagi.models.agent.Agent.get_agent_from_id', return_value=Agent(id=1)), \
#             patch('superagi.models.agent_execution.AgentExecution.get_agent_execution_from_id',
#                   return_value=AgentExecution(id=1)):
#         read_file_tool.toolkit_config.session = MagicMock()
#         file_content = read_file_tool._execute(csv_file_path)
#     assert "East" in file_content  # change "expected content" to the content you expect from CSV

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
                            # ensure your expected output matches the actual output


def test_read_file_tool_not_found(mock_os_path_exists, mock_os_makedirs, mock_get_config, mock_s3_helper, mock_partition,
                            mock_get_agent_from_id, mock_get_agent_execution_from_id):
    mock_os_path_exists.return_value = False
    mock_get_agent_from_id.return_value = MagicMock()
    mock_get_agent_execution_from_id.return_value = MagicMock()

    tool = ReadFileTool()
    file_name = "sample.txt"
    with pytest.raises(FileNotFoundError):
        tool._execute(file_name)




