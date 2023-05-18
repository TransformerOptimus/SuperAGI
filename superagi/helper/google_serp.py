import time
from pydantic import BaseModel
from webpage_extractor import WebpageExtractor
from serpapi import GoogleSearch

class GoogleSerpApiWrap:
    def __init__(self, api_key, num_results=10, num_pages=1, num_extracts=3):
        self.api_key = api_key
        self.num_results = num_results
        self.num_pages = num_pages
        self.num_extracts = num_extracts
        self.extractor = WebpageExtractor()

    def search_run(self, query):
        all_snippets = []
        links = []

        params = {
            "api_key": self.api_key,
            "engine": 'google',
            "num": self.num_results,
            "start": 0,
            "q": query
        }

        for page in range(self.num_pages):
            params["start"] = page * self.num_results
            search = GoogleSearch(params)
            results = search.get_dict()

            if "organic_results" in results:
                for result in results["organic_results"]:
                    all_snippets.append(result["snippet"])
                    links.append(result["link"])
            else:
                print("No organic results found in the response.")

        return all_snippets, links

    def get_result(self, query):
        snippets, links = self.search_run(query)

        webpages = []
        attempts = 0
        while snippets == [] and attempts < 2:
            attempts += 1
            print("Google blocked the request. Trying again...")
            time.sleep(3)
            snippets, links = self.search_run(query)

        if links:
            for i in range(0, self.num_extracts):
                time.sleep(3)
                content = self.extractor.extract_with_3k(links[i])
                attempts = 0
                while content == "" and attempts < 2:
                    attempts += 1
                    content = self.extractor.extract_with_3k(links[i])
                if content == "":
                    time.sleep(3)
                    content = self.extractor.extract_with_bs4(links[i])
                    attempts = 0
                    while content == "" and attempts < 2:
                        attempts += 1
                        content = self.extractor.extract_with_bs4(links[i])
                webpages.append(content)
        else:
            snippets = ["", "", ""]
            links = ["", "", ""]
            webpages = ["", "", ""]

        return snippets, webpages, links

