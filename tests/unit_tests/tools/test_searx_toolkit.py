import unittest
from unittest.mock import MagicMock

from superagi.tools.searx.searx import SearxSearchTool
from superagi.tools.searx.searx_toolkit import SearxSearchToolkit


class TestSearxSearchToolkit(unittest.TestCase):

    def setUp(self):
        self.toolkit = SearxSearchToolkit()

    def test_get_tools(self):
        tools = self.toolkit.get_tools()
        self.assertEqual(1, len(tools))
        self.assertIsInstance(tools[0], SearxSearchTool)

