import requests
import unittest
from unittest.mock import patch, MagicMock

from superagi.helper.serpapi import SerpApiWrap


class TestSerpApiWrap(unittest.TestCase):
    @patch.object(requests, "get")
    def test_search_success(self, mock_get):
        self.serpapi_wrap = SerpApiWrap("api_key", "engine", "no_cache", num_results=3)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "answer_box": [
                {
                    "answer": "answer_box_answer",
                    "snippet": "answer_box_snippet",
                }
            ],
            "knowledge_graph": {
                "title": "kg_title",
                "type": "kg_type",
                "description": "kg_desc",
                "fact_1": "kg_fact_1",
                "fact_2": "kg_fact_2",
                "fact_2_link": "kg_fact_2_link",
            },
            "organic_results": [
                {
                    "title": "og1_title",
                    "snippet": "og1_snippet",
                    "link": "og1_link",
                },
                {
                    "title": "og2_title",
                    "snippet": "og2_snippet",
                    "link": "og2_link",
                },
                {
                    "title": "og3_title",
                    "snippet": "og3_snippet",
                    "link": "og3_link",
                },
                {
                    "title": "og4_title",
                    "snippet": "og4_snippet",
                    "link": "og4_link",
                },
            ],
        }
        mock_get.return_value = mock_resp

        results = self.serpapi_wrap.search_run("query")

        assert results == {
            "links": ["og1_link", "og2_link", "og3_link"],
            "snippets": [
                "answer_box_answer",
                "kg_title: kg_type.",
                "kg_desc",
                "kg_title fact_1: kg_fact_1.",
                "kg_title fact_2: kg_fact_2.",
                "og1_snippet",
                "og2_snippet",
                "og3_snippet",
            ],
        }


if __name__ == "__main__":
    unittest.main()
