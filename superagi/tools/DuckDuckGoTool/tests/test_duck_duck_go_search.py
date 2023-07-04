import unittest

from duck_duck_go_search import DuckDuckGoSearchSchema, DuckDuckGoSearchTool


class DuckDuckGoSearchTestCase(unittest.TestCase):
    def setUp(self):
        self.tool = DuckDuckGoSearchTool()

    def test_tool_name(self):
        self.assertEqual(self.tool.name, "DuckDuckGoSearch")
    
    def test_tool_args_schema(self):
        self.assertEqual(self.tool.args_schema, DuckDuckGoSearchSchema)