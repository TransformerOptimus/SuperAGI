import unittest

from superagi.tools.serpapi_search.serpapi import SerpApiSearchTool
from superagi.tools.serpapi_search.serpapi_search_toolkit import SerpApiSearchToolkit


class TestSerpApiSearchToolkit(unittest.TestCase):

    def setUp(self):
        """
        Set up the test fixture.

        This method is called before each test method is executed to prepare the test environment.

        Returns:
            None
        """
        self.toolkit = SerpApiSearchToolkit()

    def test_get_tools(self):
        """
        Test the `get_tools` method of the `SerpApiSearchToolkit` class.

        It should return a list of tools, containing one instance of `SerpApiSearchTool`.

        Returns:
            None
        """

        tools = self.toolkit.get_tools()
        self.assertEqual(1, len(tools))
        self.assertIsInstance(tools[0], SerpApiSearchTool)

    def test_get_env_keys(self):
        """
        Test the `get_env_keys` method of the `SerpApiSearchToolkit` class.

        It should return three environment keys.

        Returns:
            None
        """
        env_keys = self.toolkit.get_env_keys()
        self.assertEqual(3, len(env_keys))
