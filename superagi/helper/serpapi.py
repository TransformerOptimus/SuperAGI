import requests
from typing import List

from superagi.helper.webpage_extractor import WebpageExtractor

_engine_query_key = {
    "ebay": "_nkw",
    "google_maps_reviews": "data_id",
    "google_product": "product_id",
    "google_lens": "url",
    "google_immersive_product": "page_token",
    "google_scholar_author": "author_id",
    "google_scholar_profiles": "mauthors",
    "google_related_questions": "next_page_token",
    "google_finance_markets": "trend",
    "google_health_insurance": "provider_id",
    "home_depot_product": "product_id",
    "walmart": "query",
    "walmart_product": "product_id",
    "walmart_product_reviews": "product_id",
    "yahoo": "p",
    "yahoo_images": "p",
    "yahoo_videos": "p",
    "yandex": "text",
    "yandex_images": "text",
    "yandex_videos": "text",
    "youtube": "search_query",
    "google_play_product": "product_id",
    "yahoo_shopping": "p",
    "apple_app_store": "term",
    "apple_reviews": "product_id",
    "apple_product": "product_id",
    "naver": "query",
    "yelp": "find_desc",
    "yelp_reviews": "place_id",
}


class SerpApiWrap:
    def __init__(
        self, api_key, engine, no_cache, num_results=10, num_pages=1, num_extracts=3
    ):
        """
        Initialize the GoogleSerpApiWrap class.

        Args:
            api_key (str): Google API key
            num_results (int): Number of results per page
            num_pages (int): Number of pages to search
            num_extracts (int): Number of extracts to extract from each webpage
        """
        self.api_key = api_key
        self.engine = engine or "google"
        self.no_cache = no_cache
        self.num_results = num_results
        self.num_pages = num_pages
        self.num_extracts = num_extracts
        self.extractor = WebpageExtractor()

    def search_run(self, query):
        """
        Run the SerpApi search.

        Args:
            query (str): The query to search for.

        Returns:
            list: A list of extracts from the search results.
        """

        query_key = (
            _engine_query_key[self.engine] if self.engine in _engine_query_key else "q"
        )
        params = {
            "engine": self.engine,
            query_key: query,
            "api_key": self.api_key,
            "source": "serpapi-superagi-tool",
        }

        if self.no_cache == True or self.no_cache == "true":
            params["no_cache"] = "true"

        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()

        result_json = response.json()

        return self.process_response(result_json)

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

        if results.get("error"):
            raise ValueError(f"Got error from SerpApi: {results['error']}")

        if results.get("answer_box"):
            answer_values = []
            answer_box = results.get("answer_box", {})
            if type(answer_box) == list:
                answer_box = answer_box[0]
            if answer_box.get("answer"):
                answer_values.append(answer_box.get("answer"))
            elif answer_box.get("snippet"):
                answer_values.append(answer_box.get("snippet").replace("\n", " "))
            elif answer_box.get("snippet_highlighted_words"):
                answer_values.append(
                    ", ".join(answer_box.get("snippet_highlighted_words"))
                )

            if len(answer_values) > 0:
                snippets.append("\n".join(answer_values))

        if results.get("knowledge_graph"):
            knowledge_graph = results.get("knowledge_graph", {})
            title = knowledge_graph.get("title")
            entity_type = knowledge_graph.get("type")
            if entity_type:
                snippets.append(f"{title}: {entity_type}.")
            description = knowledge_graph.get("description")
            if description:
                snippets.append(description)
            for key, value in knowledge_graph.items():
                if (
                    type(key) == str
                    and type(value) == str
                    and key not in ["title", "type", "description", "kgmid"]
                    and not key.endswith("_stick")
                    and not key.endswith("_link")
                    and not value.startswith("http")
                ):
                    snippets.append(f"{title} {key}: {value}.")

        if results.get("organic_results"):
            for result in results["organic_results"][: self.num_results]:
                if "snippet" in result:
                    snippets.append(result["snippet"])
                if "link" in result and len(links) < self.num_results:
                    links.append(result["link"])

        if len(snippets) == 0:
            return {"snippets": "No good search result was found", "links": []}

        return {"links": links, "snippets": snippets}
