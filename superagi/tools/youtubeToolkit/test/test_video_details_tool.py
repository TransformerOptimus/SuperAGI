import unittest
from json import load,dump
import sys
from os import getcwd

module_path = getcwd().replace("tests","")
sys.path.append(module_path)
from get_video_details_tool import GetVideoDetailsTool,GetVideoDetailsInput


class GetVideoDetailsToolTestCase(unittest.TestCase):
    def setUp(self):
        self.tool = GetVideoDetailsTool()

    def test_tool_name(self):
        self.assertEqual(self.tool.name, "Get Video Details")

    def test_tool_args_schema(self):
        self.assertEqual(self.tool.args_schema, GetVideoDetailsInput)

    def test_tool_description(self):
        self.assertEqual(self.tool.description, "Retrieves video details from youtube API")

    def test_execute_method(self):
        video_input = GetVideoDetailsInput(video_id="cf956pNUnFw")
        json_file= open("video_data.json","r")
        expected_output = load(json_file)
        json_file.close()
        output = self.tool._execute(video_id=video_input.video_id)
        with open("test_data.json","w") as json_file:
            dump(output,json_file)
        self.assertEqual(output,expected_output)

if __name__ == '__main__':
    unittest.main()

