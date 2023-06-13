from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from superagi.helper.browser_wrapper import browser_wrapper

from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
black_listed_elements = set(["html", "head", "title", "meta", "iframe", "body", "style", "script", "path", "svg", "br", "::marker",])
# global page_element_buffer
# page_element_buffer = {}


class ClickElementByIdSchema(BaseModel):
    element_id: str = Field(
        ..., 
        description="The ID of the HTML element to click."
        )


class ClickElementByIdTool(BaseTool):
    name = "PlaywrightClickElementByID"
    description = "A tool for clicking an element by its ID using Playwright.clicks an element. Specify the id with the unique id received from the get_dom command. CRITICAL: The ID must be the integer id from the get_dom command. It should execute after getting the DOM"
    args_schema: Type[ClickElementByIdSchema] = ClickElementByIdSchema

    def _execute(self, element_id: str) -> str:
        page_element_buffer = browser_wrapper.page_element_buffer
        client = browser_wrapper.client
        page = browser_wrapper.page

        # Inject javascript into the page which removes the target= attribute from all links
        js = """
        links = document.getElementsByTagName("a");
        for (var i = 0; i < links.length; i++) {
            links[i].removeAttribute("target");
        }
        """
        page.evaluate(js)

        element = page_element_buffer.get(int(element_id))
        if element:
            x = element.get("center_x")
            y = element.get("center_y")

            page.mouse.click(x, y)
        else:
            return "Could not find element"

        return "Successfully clicked!"