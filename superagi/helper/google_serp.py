import os
import sys
import time
from typing import Any

from pydantic import BaseModel
from serpapi import GoogleSearch

from superagi.helper.webpage_extractor import WebpageExtractor

class GoogleSerpApiWrap:
    def __init__(self, api_key, num_results=10, num_pages=1, num_extracts=3):
        self.api_key = api_key
        self.num_results = num_results
        self.num_pages = num_pages
        self.num_extracts = num_extracts
        self.extractor = WebpageExtractor()

    def search_run(self, query):
        params = {
            "api_key": self.api_key,
            "engine": 'google',
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "q": query
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        response = self.process_response(results)
        return response

    @staticmethod
    def process_response(api_response: dict) -> str:
        result = ""
        if "error" in api_response.keys():
            raise ValueError(f"Got error from SerpAPI: {api_response['error']}")
        if "answer_box" in api_response.keys():
            if "answer" in api_response["answer_box"].keys():
                result = api_response["answer_box"]["answer"]
            elif "snippet" in api_response["answer_box"].keys():
                result = api_response["answer_box"]["snippet"]
            elif "snippet_highlighted_words" in api_response["answer_box"].keys():
                result = api_response["answer_box"]["snippet_highlighted_words"][0]
        elif "sports_results" in api_response.keys() and "game_spotlight" in api_response["sports_results"].keys():
            result = api_response["sports_results"]["game_spotlight"]
        elif "knowledge_graph" in api_response.keys() and "description" in api_response["knowledge_graph"].keys():
            result = api_response["knowledge_graph"]["description"]
        elif "snippet" in api_response["organic_results"][0].keys():
            result = api_response["organic_results"][0]["snippet"]
        elif "answer_box" in api_response.keys() and "answer" in api_response["answer_box"].keys():
            result = api_response["answer_box"]["answer"]
        elif "snippet" in api_response["organic_results"][0].keys():
            result = api_response["organic_results"][0]["snippet"]
        else:
            result = "No good search result found"
        return result
