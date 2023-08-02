from unittest.mock import Mock

import pytest

from superagi.resource_manager.file_manager import FileManager
from superagi.tools.code.write_code import CodingTool
from superagi.tools.tool_response_query_manager import ToolResponseQueryManager


class MockBaseLlm:
    def chat_completion(self, messages, max_tokens):
        return {"content": "File1.py\n```python\nprint('Hello World')\n```\n\nFile2.py\n```python\nprint('Hello again')\n```"}

    def get_model(self):
        return "gpt-3.5-turbo"

class TestCodingTool:

    @pytest.fixture
    def tool(self):
        tool = CodingTool()
        tool.llm = MockBaseLlm()
        tool.resource_manager = Mock(spec=FileManager)
        tool.tool_response_manager = Mock(spec=ToolResponseQueryManager)
        return tool

    def test_execute(self, tool):
        tool.resource_manager.write_file.return_value = "File write successful"
        tool.tool_response_manager.get_last_response.return_value = "Mocked Spec"

        response = tool._execute("Test spec description")
        assert response == "File1.py\n```python\nprint('Hello World')\n```\n\nFile2.py\n```python\nprint('Hello again')\n```\n Codes generated and saved successfully in File1.py, File2.py"

        tool.resource_manager.write_file.assert_any_call("README.md", 'File1.py\n')
        tool.resource_manager.write_file.assert_any_call("File1.py", "print('Hello World')\n")
        tool.resource_manager.write_file.assert_any_call("File2.py", "print('Hello again')\n")
        tool.tool_response_manager.get_last_response.assert_called_once_with("WriteSpecTool")