from typing import Type

from pydantic import BaseModel, Field

from superagi.helper.webpage_extractor import WebpageExtractor
from superagi.tools.base_tool import BaseTool


class WebScraperSchema(BaseModel):
    website_url: str = Field(
        ...,
        description="website url",
    )


class WebScraperTool(BaseTool):
    name = "WebScraperTool"
    description = (
        "Used to scrape website urls and extract text content"
    )
    args_schema: Type[WebScraperSchema] = WebScraperSchema

    def _execute(self, website_url: str) -> tuple:
        content = WebpageExtractor().extract_with_bs4(website_url)
        return content[:1000]