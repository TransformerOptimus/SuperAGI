import json
from typing import Type, Optional

from pydantic import BaseModel, Field

from superagi.helper.google_search import GoogleSearchWrap
from superagi.helper.token_counter import TokenCounter
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool


class GoogleSearchSchema(BaseModel):
    query: str = Field(
        ...,
        description="The search query for Google search.",
    )

class GoogleSearchTool(BaseTool):
    """
    Google Search tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    llm: Optional[BaseLlm] = None
    name = "GoogleSearch"
    description = (
        "A tool for performing a Google search and extracting snippets and webpages."
        "Input should be a search query."
    )
    args_schema: Type[GoogleSearchSchema] = GoogleSearchSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, query: str) -> tuple:
        """
        Execute the Google search tool.

        Args:
            query : The query to search for.

        Returns:
            Search result summary along with related links
        """
        api_key = self.get_tool_config("GOOGLE_API_KEY")
        search_engine_id = self.get_tool_config("SEARCH_ENGINE_ID")
        num_results = 10
        num_pages = 1
        num_extracts = 3

        google_search = GoogleSearchWrap(api_key, search_engine_id, num_results, num_pages, num_extracts)
        snippets, webpages, links = google_search.get_result(query)

        results = []
        i = 0
        for webpage in webpages:
            results.append({"title": snippets[i], "body": webpage, "links": links[i]})
            i += 1
            if TokenCounter.count_text_tokens(json.dumps(results)) > 3000:
                break
        summary = self.summarise_result(query, results)
        links = [result["links"] for result in results if len(result["links"]) > 0]
        if len(links) > 0:
            return summary + "\n\nLinks:\n" + "\n".join("- " + link for link in links[:3])
        return summary

    def summarise_result(self, query, snippets):
        """
        Summarise the result of a Google search.

        Args:
            query : The query to search for.
            snippets (list): A list of snippets from the search.

        Returns:
            A summary of the search result.
        """
        summarize_prompt ="""Summarize the following text `{snippets}`
            Write a concise or as descriptive as necessary and attempt to
            answer the query: `{query}` as best as possible. Use markdown formatting for
            longer responses."""

        summarize_prompt = summarize_prompt.replace("{snippets}", str(snippets))
        summarize_prompt = summarize_prompt.replace("{query}", query)

        messages = [{"role": "system", "content": summarize_prompt}]
        result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
        return result["content"]
