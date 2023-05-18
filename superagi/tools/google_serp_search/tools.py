from typing import Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from helper.google_serp import GoogleSerpApiWrap  # Import the GoogleSerpApiWrap class
import os
import json

class GoogleSerpSchema(BaseModel):
    query: str = Field(
        ...,
        description="The search query for Google SERP.",
    )


class GoogleSerpTool(BaseTool):
    name = "GoogleSerp"
    description = (
        "A tool for performing a Google SERP search and extracting snippets and webpages."
        "Input should be a search query."
    )
    args_schema: Type[GoogleSerpSchema] = GoogleSerpSchema

    def execute(self, query: str) -> tuple:
        api_key = os.environ.get("SERP_API_KEY")
        num_results = 10
        num_pages = 1
        num_extracts = 3

        serp_api = GoogleSerpApiWrap(api_key, num_results, num_pages, num_extracts)
        snippets, webpages, links = serp_api.get_result(query)

        result = {
            "snippets": snippets,
            "webpages": webpages,
            "links": links
        }

        return json.dumps(result)