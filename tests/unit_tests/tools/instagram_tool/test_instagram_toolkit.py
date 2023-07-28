import pytest
from superagi.tools.instagram_tool.instagram import InstagramTool
from superagi.tools.instagram_tool.instagram_toolkit import InstagramToolkit

class TestInstagramToolKit:
    def setup_method(self):
        """
        Set up the test fixture.

        This method is called before each test method is executed to prepare the test environment.

        Returns:
            None
        """
        self.toolkit = InstagramToolkit()

    def test_get_tools(self):
        """
        Test the `get_tools` method of the `DuckDuckGoToolkit` class.

        It should return a list of tools, containing one instance of `DuckDuckGoSearchTool`.

        Returns:
            None
        """
        tools = self.toolkit.get_tools()
        assert len(tools) == 1
        assert isinstance(tools[0], InstagramTool)

    def test_get_env_keys(self):
        """
        Test the `get_env_keys` method of the `DuckDuckGoToolkit` class.

        It should return an empty list of environment keys.

        Returns:
            None
        """
        env_keys = self.toolkit.get_env_keys()
        assert len(env_keys) == 2
