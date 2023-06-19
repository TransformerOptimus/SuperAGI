import requests
import time
from pydantic import BaseModel
from superagi.lib.logger import logger

from superagi.helper.webpage_extractor import WebpageExtractor


class GoogleSearchWrap:

    def __init__(self, api_key, search_engine_id, num_results=3, num_pages=1, num_extracts=3):
        """
        Initialize the GoogleSearchWrap class.

        Args:
            api_key (str): Google API key
            search_engine_id (str): Google Search Engine ID
            num_results (int): Number of results per page
            num_pages (int): Number of pages to search
            num_extracts (int): Number of extracts to extract from each webpage
        """

        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.num_results = num_results
        self.num_pages = num_pages
        self.num_extracts = num_extracts
        self.extractor = WebpageExtractor()

    def search_run(self, query):
        """
        Run the Google search.

        Args:
            query (str): The query to search for.

        Returns:
            list: A list of extracts from the search results.
        """
        all_snippets = []
        links = []
        for page in range(1, self.num_pages * self.num_results, self.num_results):
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": self.num_results,
                "start": page
            }
            response = requests.get(url, params=params, timeout=100)

            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if "items" in json_data:
                        for item in json_data["items"]:
                            all_snippets.append(item["snippet"])
                            links.append(item["link"])
                    else:
                        logger.info("No items found in the response.")
                except ValueError as e:
                    logger.error(f"Error while parsing JSON data: {e}")
            else:
                logger.error(f"Error: {response.status_code}")

        return all_snippets, links, response.status_code

    def get_result(self, query):
        """
        Get the result of the Google search.

        Args:
            query (str): The query to search for.

        Returns:
            list: A list of extracts from the search results.
        """
        snippets, links, error_code = self.search_run(query)

        webpages = []
        attempts = 0
        while snippets == [] and attempts < 2:
            attempts += 1
            logger.info("Google blocked the request. Trying again...")
            time.sleep(3)
            snippets, links, error_code = self.search_run(query)

        if links:
            for i in range(0, self.num_extracts):
                time.sleep(3)
                content = ""
                # content = self.extractor.extract_with_3k(links[i])
                # attempts = 0
                # while content == "" and attempts < 2:
                #     attempts += 1
                #     content = self.extractor.extract_with_3k(links[i])
                content = self.extractor.extract_with_bs4(links[i])
                max_length = len(' '.join(content.split(" ")[:500]))
                content = content[:max_length]
                attempts = 0
                while content == "" and attempts < 2:
                    attempts += 1
                    content = self.extractor.extract_with_bs4(links[i])
                    content = content[:max_length]
                webpages.append(content)
        else:
            snippets = []
            links = []
            webpages = []

        return snippets, webpages, links