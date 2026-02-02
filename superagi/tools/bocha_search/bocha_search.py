from typing import Type, Optional, Any
from pydantic import BaseModel, Field
import aiohttp
from superagi.helper.error_handler import ErrorHandler
from superagi.llms.base_llm import BaseLlm
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.tools.base_tool import BaseTool
import os
import requests

import json


class BoChaSchema(BaseModel):
    query: str = Field(
        ...,
        description="The search query for BoCha.",
    )


class BoChaTool(BaseTool):
    """
    BoCha Search tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    llm: Optional[BaseLlm] = None
    name = "BoCha"
    agent_id: int = None
    agent_execution_id: int = None
    description = (
        "A tool for performing a BoCha search and extracting snippets and webpages."
        "Input should be a search query."
    )
    args_schema: Type[BoChaSchema] = BoChaSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, query: str) -> tuple:
        """
        Execute the BoCha search tool.

        Args:
            query : The query to search for.

        Returns:
            Search result summary along with related links
        """
        api_key = self.get_tool_config("BoCha_API_KEY")
        url = 'https://api.bochaai.com/v1/web-search'
        headers = {
            'Authorization': f'Bearer {api_key}',  # 请替换为你的API密钥
            'Content-Type': 'application/json'
        }
        data = {
            "query": query,
            "freshness": "noLimit",  # 搜索的时间范围，
            "summary": True,  # 是否返回长文本摘要
            # "count": count
        }

        response = requests.post(url, headers=headers, json=data).json()
        snippets: list[str] = []
        for result in response["data"]["webPages"]["value"]:
            if "snippet" in result:
                snippets.append(result["snippet"])

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

        if 'error' in result and result['message'] is not None:
            ErrorHandler.handle_openai_errors(self.toolkit_config.session, self.agent_id, self.agent_execution_id,
                                              result['message'])
        return result["content"]