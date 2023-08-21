from typing import Type, Optional
from pydantic import BaseModel, Field
from superagi.helper.serpapi import SerpApiWrap
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool


class SerpApiSearchSchema(BaseModel):
    query: str = Field(
        ...,
        description="The search query for SerpApi.",
    )


class SerpApiSearchTool(BaseTool):
    """
    SerpApi Search tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """

    llm: Optional[BaseLlm] = None
    name = "SerpApi Search"
    description = (
        "A tool for performing a Google/Bing/Yahoo!/Baidu/DuckDuckGo/Yandex/Naver/... search and extracting snippets and webpages."
        "Input should be a search query."
    )
    args_schema: Type[SerpApiSearchSchema] = SerpApiSearchSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, query: str) -> tuple:
        """
        Execute the SerpApi search tool.

        Args:
            query : The query to search for.

        Returns:
            Search result summary along with related links
        """
        api_key = self.get_tool_config("SERPAPI_API_KEY")
        engine = self.get_tool_config("SERPAPI_ENGINE")
        no_cache = self.get_tool_config("SERPAPI_NO_CACHE")
        serp_api = SerpApiWrap(api_key, engine, no_cache)
        response = serp_api.search_run(query)
        summary = self.summarise_result(query, response["snippets"])
        if response["links"]:
            return (
                summary
                + "\n\nLinks:\n"
                + "\n".join("- " + link for link in response["links"][:3])
            )
        return summary

    def summarise_result(self, query, snippets):
        """
        Summarise the result of the SerpApi search.

        Args:
            query : The query to search for.
            snippets : The snippets from the SerpApi search.

        Returns:
            A summary of the result.
        """
        summarize_prompt = """Summarize the following text `{snippets}`
            Write a concise or as descriptive as necessary and attempt to
            answer the query: `{query}` as best as possible. Use markdown formatting for
            longer responses."""

        summarize_prompt = summarize_prompt.replace("{snippets}", str(snippets))
        summarize_prompt = summarize_prompt.replace("{query}", query)

        messages = [{"role": "system", "content": summarize_prompt}]
        result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
        return result["content"]
