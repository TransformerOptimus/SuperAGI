import unittest

from greetings_tool import GreetingsTool
from greetings_toolkit import GreetingsToolkit


class GreetingsToolkitTests(unittest.TestCase):
    def setUp(self):
        self.toolkit = GreetingsToolkit()

    def test_get_tools_returns_list_of_tools(self):
        tools = self.toolkit.get_tools()
        self.assertIsInstance(tools, list)
        self.assertTrue(all(isinstance(tool, GreetingsTool) for tool in tools))

    def test_get_env_keys_returns_list_of_strings(self):
        env_keys = self.toolkit.get_env_keys()
        self.assertIsInstance(env_keys, list)
        self.assertTrue(all(isinstance(key, str) for key in env_keys))

    def test_toolkit_has_name_and_description(self):
        self.assertEqual(self.toolkit.name, "Greetings Toolkit")
        self.assertEqual(self.toolkit.description, "Greetings Tool kit contains all tools related to Greetings")
