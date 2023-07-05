import unittest
from superagi.tools.duck_duck_go.duck_duck_go_search_toolkit import DuckDuckGoToolkit
from superagi.tools.duck_duck_go.duck_duck_go_search import DuckDuckGoSearchTool

class DuckDuckGoSearchToolKitTest(unittest.TestCase):
    def setUp(self):
        """
        Set up the test fixture.

        This method is called before each test method is executed to prepare the test environment.

        Returns:
            None
        """
        self.toolkit = DuckDuckGoToolkit()

    def test_get_tools(self):
        """
        Test the `get_tools` method of the `SearxSearchToolkit` class.

        It should return a list of tools, containing one instance of `SearxSearchTool`.

        Returns:
            None
        """

        tools = self.toolkit.get_tools()
        self.assertEqual(1, len(tools))
        self.assertIsInstance(tools[0], DuckDuckGoSearchTool)

    def test_get_env_keys(self):
        """
        Test the `get_env_keys` method of the `SearxSearchToolkit` class.

        It should return an empty list of environment keys.

        Returns:
            None
        """
        env_keys = self.toolkit.get_env_keys()
        self.assertEqual(0, len(env_keys))

if __name__ == '__main__':
    unittest.main()

