from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from superagi.helper.browser_wrapper import browser_wrapper

from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field, PrivateAttr


class InputTextByIdAndPressEnterSchema(BaseModel):
    element_id: str = Field(
        ..., 
        description="The ID of the HTML element to input text."
        )
    text: str = Field(
        ..., 
        description="The text to input into the element."
        )


class InputTextByIdAndPressEnterTool(BaseTool):
    name = "PlaywrightInputTextByIDAndPressEnter"
    description = (
        "A tool for inputting text into an element by its ID and pressing Enter using Playwright."
    )
    args_schema: Type[InputTextByIdAndPressEnterSchema] = InputTextByIdAndPressEnterSchema

    def _execute(self, element_id: str, text: str) -> str:
        page = browser_wrapper.page
        def click(id):
            # Inject javascript into the page which removes the target= attribute from all links
            js = """
            links = document.getElementsByTagName("a");
            for (var i = 0; i < links.length; i++) {
                links[i].removeAttribute("target");
            }
            """
            browser_wrapper.page.evaluate(js)

            element = browser_wrapper.page_element_buffer.get(int(id))
            if element:
                x = element.get("center_x")
                y = element.get("center_y")
                
                browser_wrapper.page.mouse.click(x, y)
            else:
                return "Could not find element"

            return "Successfully clicked!"

        click(int(element_id))
        page.keyboard.type(text)
        page.keyboard.press("Enter")

        return f"Inputted text '{text}', and pressed enter!"