import pytest
from unittest.mock import Mock, MagicMock
from superagi.tools.code.improve_code import ImproveCodeTool

@pytest.fixture
def mock_improve_code_tool():
    improve_code_tool = ImproveCodeTool()
    improve_code_tool.resource_manager = Mock()
    improve_code_tool.llm = Mock()
    return improve_code_tool

def test_execute(mock_improve_code_tool):
    mock_improve_code_tool.resource_manager.get_files.return_value = ['test1', 'test2']
    mock_improve_code_tool.resource_manager.read_file.return_value = "test file content"
    mock_improve_code_tool.llm.chat_completion.return_value = {
        "response":
            {
                "choices":
                    [
                        {
                            "message":
                                {
                                    "content": "```\nimproved code\n```"
                                }
                        }
                    ]
            }
    }
    mock_improve_code_tool.resource_manager.write_file.return_value = "file saved successfully"

    assert mock_improve_code_tool._execute() == "All codes improved and saved successfully in: test1 test2"

def test_execute_with_error(mock_improve_code_tool):
    mock_improve_code_tool.resource_manager.get_files.return_value = ['test1']
    mock_improve_code_tool.resource_manager.read_file.return_value = "test file content"
    mock_improve_code_tool.llm.chat_completion.return_value = {
        "response":
            {
                "choices":
                    [
                        {
                            "message":
                                {
                                    "content": "```\nimproved code\n```"
                                }
                        }
                    ]
            }
    }
    mock_improve_code_tool.resource_manager.write_file.return_value = "Error: Could not save file"

    assert mock_improve_code_tool._execute() == "Error: Could not save file"
