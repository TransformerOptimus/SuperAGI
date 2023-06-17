import asyncio
from typing import Any, List

import aiohttp

from superagi.config.config import get_config
from superagi.helper.webpage_extractor import WebpageExtractor


class GoogleSerpApiWrap:
    def __init__(self, api_key, num_results=10, num_pages=1, num_extracts=3):
        """
        Initialize the GoogleSerpApiWrap class.

        Args:
            api_key (str): Google API key
            num_results (int): Number of results per page
            num_pages (int): Number of pages to search
            num_extracts (int): Number of extracts to extract from each webpage
        """
        self.api_key = api_key
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
        results = asyncio.run(self.fetch_serper_results(query=query))
        response = self.process_response(results)
        return response

    async def fetch_serper_results(self,
                                   query: str, search_type: str = "search"
                                   ) -> dict[str, Any]:
        """
        Fetch the search results from the SerpApi.

        Args:
            query (str): The query to search for.
            search_type (str): The type of search to perform.

        Returns:
            dict: The search results.
        """
        headers = {
            "X-API-KEY": self.api_key or "",
            "Content-Type": "application/json",
        }
        params = {"q": query,}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"https://google.serper.dev/{search_type}", headers=headers, params=params
            ) as response:
                response.raise_for_status()
                search_results = await response.json()
                return search_results

    def process_response(self, results) -> str:
        """
        Process the search results.

        Args:
            results (dict): The search results.

        Returns:
            str: The processed search results.
        """
        snippets: List[str] = []
        links: List[str] = []

        if results.get("answerBox"):
            answer_values = []
            answer_box = results.get("answerBox", {})
            if answer_box.get("answer"):
                answer_values.append(answer_box.get("answer"))
            elif answer_box.get("snippet"):
                answer_values.append(answer_box.get("snippet").replace("\n", " "))
            elif answer_box.get("snippetHighlighted"):
                answer_values.append(", ".join(answer_box.get("snippetHighlighted")))

            if len(answer_values) > 0:
                snippets.append("\n".join(answer_values))

        if results.get("knowledgeGraph"):
            knowledge_graph = results.get("knowledgeGraph", {})
            title = knowledge_graph.get("title")
            entity_type = knowledge_graph.get("type")
            if entity_type:
                snippets.append(f"{title}: {entity_type}.")
            description = knowledge_graph.get("description")
            if description:
                snippets.append(description)
            for attribute, value in knowledge_graph.get("attributes", {}).items():
                snippets.append(f"{title} {attribute}: {value}.")

        for result in results["organic"][:self.num_results]:
            if "snippet" in result:
                snippets.append(result["snippet"])
            if "link" in result and len(links) < self.num_results:
                links.append(result["link"])
            for attribute, value in result.get("attributes", {}).items():
                snippets.append(f"{attribute}: {value}.")

        if len(snippets) == 0:
            return {"snippets": "No good Google Search Result was found", "links": []}

        return {"links": links, "snippets": snippets}
