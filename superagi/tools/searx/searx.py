from typing import Type, Optional
from pydantic import BaseModel, Field
from superagi.helper.error_handler import ErrorHandler
from superagi.llms.base_llm import BaseLlm
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.tools.base_tool import BaseTool
from superagi.tools.searx.search_scraper import search_results


class SearxSearchSchema(BaseModel):
    query: str = Field(
        ...,
        description="The search query for the Searx search engine.",
    )

class SearxSearchTool(BaseTool):
    """
    Searx Search tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    llm: Optional[BaseLlm] = None
    name = "SearxSearch"
    agent_id:int =None
    agent_execution_id:int =None
    description = (
        "A tool for performing a Searx search and extracting snippets and webpages."
        "Input should be a search query."
    )
    args_schema: Type[SearxSearchSchema] = SearxSearchSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, query: str) -> tuple:
        """
        Execute the Searx search tool.

        Args:
            query : The query to search for.

        Returns:
            Snippets from the Searx search.
        """
        snippets = search_results(query)
        summary = self.summarise_result(query, snippets)

        return summary

    def summarise_result(self, query, snippets):
        """
        Summarise the result of the Searx search.

        Args:
            query : The query to search for.
            snippets : The snippets from the Searx search.

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
        
        if 'error' in result and result['message'] is not None:
            ErrorHandler.handle_openai_errors(self.toolkit_config.session, self.agent_id, self.agent_execution_id, result['message'])
        return result["content"]
