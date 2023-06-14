from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from superagi.helper.browser_wrapper import browser_wrapper

from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field, PrivateAttr


class GetURLSchema(BaseModel):
    pass


class GetURLTool(BaseTool):
    name = "PlaywrightGetURL"
    description = "A tool for getting the current URL using Playwright.Retrieves the current url that the web_interaction plugin is on"
    args_schema: Type[GetURLSchema] = GetURLSchema

    def _execute(self) -> str:
        page = browser_wrapper.page

        try:
            current_url = page.url
            return current_url
        except:
            return "Error retrieving current URL."