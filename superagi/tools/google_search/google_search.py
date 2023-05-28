from typing import Type, List
from pydantic import BaseModel, Field

from superagi.helper.google_search import GoogleSearchWrap
from superagi.helper.token_counter import TokenCounter
from superagi.tools.base_tool import BaseTool
import os
import json
from superagi.config.config import get_config



class GoogleSearchSchema(BaseModel):
    query: str = Field(
        ...,
        description="The search query for Google search.",
    )


class GoogleSearchTool(BaseTool):
    name = "GoogleSearch"
    description = (
        "A tool for performing a Google search and extracting snippets and webpages."
        "Input should be a search query."
    )
    args_schema: Type[GoogleSearchSchema] = GoogleSearchSchema

    def _execute(self, query: str) -> tuple:
        api_key = get_config("GOOGLE_API_KEY")
        search_engine_id = get_config("SEARCH_ENGINE_ID")
        num_results = 10
        num_pages = 1
        num_extracts = 3

        print("query: ", query)
        google_search = GoogleSearchWrap(api_key, search_engine_id, num_results, num_pages, num_extracts)
        snippets, webpages, links = google_search.get_result(query)

        results = []
        i = 0
        for webpage in webpages:
            results.append({"title": snippets[i], "body": webpage, "link": links[i]})
            i += 1
            if TokenCounter.count_text_tokens(json.dumps(results)) > self.max_token_limit:
                break

        return results