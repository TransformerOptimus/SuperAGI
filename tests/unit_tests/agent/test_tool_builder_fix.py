
import unittest
from unittest.mock import MagicMock, patch
from superagi.agent.tool_builder import ToolBuilder
from superagi.models.tool import Tool

class TestToolBuilderFix(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.agent_id = 1
        self.agent_execution_id = 1
        self.tool_builder = ToolBuilder(self.session, self.agent_id, self.agent_execution_id)

    def test_build_tool_none(self):
        """Test that ValueError is raised when tool is None"""
        with self.assertRaises(ValueError) as context:
            self.tool_builder.build_tool(None)
        self.assertEqual(str(context.exception), "Tool object is None")

    @patch('os.path.exists')
    def test_build_tool_directory_not_found(self, mock_exists):
        """Test that ValueError is raised with detailed message when directory is missing"""
        # Mock os.path.exists to always return False (directory not found)
        mock_exists.return_value = False
        
        tool = Tool()
        tool.folder_name = "non_existent_tool"
        tool.file_name = "tools.py"
        tool.class_name = "MyTool"

        with self.assertRaises(ValueError) as context:
            self.tool_builder.build_tool(tool)
        
        expected_msg = "Tool directory not found for tool: non_existent_tool. Searched in: superagi/tools, superagi/tools/external_tools, superagi/tools/marketplace_tools"
        self.assertEqual(str(context.exception), expected_msg)

if __name__ == '__main__':
    unittest.main()
