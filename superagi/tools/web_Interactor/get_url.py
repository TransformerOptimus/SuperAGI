from pydantic import BaseModel
from superagi.tools.base_tool import BaseTool
from superagi.helper.browser_wrapper import browser_wrapper


class GetURLSchema(BaseModel):
    pass


class GetURLTool(BaseTool):
    name = "Get URL"
    description = "A tool for getting the current URL using Playwright.Retrieves the current url that the web_interaction plugin is on"
    args_schema = GetURLSchema

    def _execute(self) -> str:
        page = browser_wrapper.page

        try:
            current_url = page.url
            return current_url
        except:
            return "Error retrieving current URL."