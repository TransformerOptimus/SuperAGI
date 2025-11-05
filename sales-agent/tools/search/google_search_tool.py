import requests
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from tools.base_tool import BaseTool
from config.config import config


class GoogleSearchSchema(BaseModel):
    """Schema for Google search"""
    query: str = Field(
        ...,
        description="Search query to find information about companies or prospects"
    )
    num_results: int = Field(
        default=5,
        description="Number of search results to return (max 10)"
    )


class GoogleSearchTool(BaseTool):
    """
    Google Search Tool for company research

    Searches Google to gather information about companies and prospects
    for personalized outreach.
    """

    name = "google_search"
    description = (
        "Search Google for information about a company or prospect. "
        "Use this to research company background, recent news, achievements, "
        "and relevant information for personalized outreach."
    )
    args_schema = GoogleSearchSchema

    def execute(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Execute Google search

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of search result dictionaries
        """
        if not config.GOOGLE_API_KEY or not config.GOOGLE_SEARCH_ENGINE_ID:
            # Fallback to DuckDuckGo if Google not configured
            return self._duckduckgo_search(query, num_results)

        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": config.GOOGLE_API_KEY,
                "cx": config.GOOGLE_SEARCH_ENGINE_ID,
                "q": query,
                "num": min(num_results, 10)
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            results = []

            if "items" in data:
                for item in data["items"]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", "")
                    })

            return results

        except Exception as e:
            print(f"Google Search error: {str(e)}")
            return self._duckduckgo_search(query, num_results)

    def _duckduckgo_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """
        Fallback search using DuckDuckGo

        Args:
            query: Search query
            num_results: Number of results

        Returns:
            List of search results
        """
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=num_results)
                for result in search_results:
                    results.append({
                        "title": result.get("title", ""),
                        "link": result.get("href", ""),
                        "snippet": result.get("body", "")
                    })

            return results

        except ImportError:
            # If duckduckgo_search not installed, return basic result
            return [{
                "title": f"Search: {query}",
                "link": f"https://www.google.com/search?q={query.replace(' ', '+')}",
                "snippet": "Google Search API or DuckDuckGo not configured. Please add API credentials."
            }]
        except Exception as e:
            return [{
                "error": f"Search failed: {str(e)}"
            }]
