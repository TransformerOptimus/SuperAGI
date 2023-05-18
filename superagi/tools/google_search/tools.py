from typing import Type, List
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from helper.google_search import GoogleSearchWrap
import os
import json


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

    def execute(self, query: str) -> tuple:
        api_key = os.environ.get("GOOGLE_API_KEY")
        search_engine_id = os.environ.get("SEARCH_ENGINE_ID")
        num_results = 10
        num_pages = 1
        num_extracts = 3

        google_search = GoogleSearchWrap(api_key, search_engine_id, num_results, num_pages, num_extracts)
        snippets, webpages, links = google_search.get_result(query)

        result = {
            "snippets": snippets,
            "webpages": webpages,
            "links": links
        }

        return json.dumps(result)
    

# Import necessary modules
import os
import json

# Define the environment variables
os.environ["GOOGLE_API_KEY"] = "AIzaSyCinJK2sB7Ky-3DmmsSNWFn5leAwev-9Hs"
os.environ["SEARCH_ENGINE_ID"] = "e6fbba732ab9e49fd"

# Create an instance of GoogleSearchTool
google_search_tool = GoogleSearchTool()

# Define the search query
query = "Python programming"

# Execute the Google search tool
result = google_search_tool.execute(query)

# Print the result
print(result)
