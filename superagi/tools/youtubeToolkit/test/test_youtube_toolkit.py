import unittest
from os import getcwd
import sys
module_path = getcwd().replace("tests","")
sys.path.append(module_path)

from get_video_details_tool import GetVideoDetailsTool
from youtube_toolkit import YoutubeToolkit


class YoutubeToolkitTests(unittest.TestCase):
    def setUp(self):
        self.toolkit = YoutubeToolkit()

    def test_get_tools_returns_list_of_tools(self):
        tools = self.toolkit.get_tools()
        self.assertIsInstance(tools, list)
        self.assertTrue(all(isinstance(tool, GetVideoDetailsTool) for tool in tools))

    def test_toolkit_has_name_and_description(self):
        self.assertEqual(self.toolkit.name, "Youtube Toolkit")
        self.assertEqual(self.toolkit.description, "Youtube Toolkit contains tools for youtube channel and youtube videos")


if __name__ == '__main__':
    unittest.main()