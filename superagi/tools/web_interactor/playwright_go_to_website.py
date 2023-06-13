from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from superagi.helper.browser_wrapper import browser_wrapper

from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

class GoToWebsiteSchema(BaseModel):
    url: str = Field(
        ..., 
        description="The URL to navigate to."
        )


class GoToWebsiteTool(BaseTool):
    name = "PlaywrightGoToWebsite"
    description = (
        "A tool for navigation to a specified URL using the Playwright browser.Goes to a website in the web interaction plugin. Must be ran after starting the browser and before attempting to interact with a website"
    )
    args_schema: Type[GoToWebsiteSchema] = GoToWebsiteSchema

    def _execute(self, url: str) -> str:
        page = browser_wrapper.page
        client = browser_wrapper.client

        try:
            page.goto(url=url if "://" in url else "http://" + url)
            client = page.context.new_cdp_session(page)
        except:
            return "Failed to go to URL, please try again and make sure the URL is correct."

        return "Navigated to URL " + url