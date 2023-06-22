from unittest.mock import Mock, patch
import pytest

from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.manager import ResourceManager
from superagi.tools.code.write_code import CodingTool

class MockBaseLlm:
    def chat_completion(self, messages, max_tokens):
        return {"content": "File1.py\n```python\nprint('Hello World')\n```\n\nFile2.py\n```python\nprint('Hello again')\n```"}

class TestCodingTool:

    @pytest.fixture
    def tool(self):
        tool = CodingTool()
        tool.llm = MockBaseLlm()
        tool.resource_manager = Mock()
        return tool

    def test_execute(self, tool):
        tool.resource_manager.write_file = Mock()
        tool.resource_manager.write_file.return_value = "File write successful"
        response = tool._execute("Test spec description")
        assert response == "File1.py\n```python\nprint('Hello World')\n```\n\nFile2.py\n```python\nprint('Hello again')\n```\n Codes generated and saved successfully in File1.py, File2.py"
        tool.resource_manager.write_file.assert_any_call("README.md", 'File1.py\n')
        tool.resource_manager.write_file.assert_any_call("File1.py", "print('Hello World')\n")
        tool.resource_manager.write_file.assert_any_call("File2.py", "print('Hello again')\n")