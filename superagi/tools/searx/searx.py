from typing import Type, Optional
from pydantic import BaseModel, Field
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool
from superagi.tools.searx.search_scraper import search_results


class SearxSearchSchema(BaseModel):
    query: str = Field(
        ...,
        description="The search query for the Searx search engine.",
    )

class SearxSearchTool(BaseTool):
    llm: Optional[BaseLlm] = None
    name = "SearxSearch"
    description = (
        "A tool for performing a Searx search and extracting snippets and webpages."
        "Input should be a search query."
    )
    args_schema: Type[SearxSearchSchema] = SearxSearchSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, query: str) -> tuple:
        snippets = search_results(query)
        summary = self.summarise_result(query, snippets)

        return summary

    def summarise_result(self, query, snippets):
        summarize_prompt = """Summarize the following text `{snippets}`
            Write a concise or as descriptive as necessary and attempt to
            answer the query: `{query}` as best as possible. Use markdown formatting for
            longer responses."""

        summarize_prompt = summarize_prompt.replace("{snippets}", str(snippets))
        summarize_prompt = summarize_prompt.replace("{query}", query)

        messages = [{"role": "system", "content": summarize_prompt}]
        result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
        return result["content"]
