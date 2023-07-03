import unittest

from greetings_tool import GreetingsTool, GreetingsInput


class GreetingsToolTestCase(unittest.TestCase):
    def setUp(self):
        self.tool = GreetingsTool()

    def test_tool_name(self):
        self.assertEqual(self.tool.name, "Greetings Tool")

    def test_tool_args_schema(self):
        self.assertEqual(self.tool.args_schema, GreetingsInput)

    def test_tool_description(self):
        self.assertEqual(self.tool.description, "Sends a Greeting Message")

    def test_execute_method(self):
        greetings_input = GreetingsInput(greetings="Hello")
        expected_output = "Hello" + "\n" + self.tool.get_tool_config('FROM')
        output = self.tool._execute(greetings=greetings_input.greetings)
        self.assertEqual(output, expected_output)
