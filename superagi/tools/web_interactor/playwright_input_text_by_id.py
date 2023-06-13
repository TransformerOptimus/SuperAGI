from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.helper.browser_wrapper import browser_wrapper


class InputTextByIdSchema(BaseModel):
    element_id: str = Field(..., description="The ID of the HTML element to input text.")
    text: str = Field(..., description="The text to input into the element.")


class InputTextByIdTool(BaseTool):
    
    name = "PlaywrightInputTextByID"
    description = "A tool for inputting text into an element by its ID using Playwright."
    args_schema = InputTextByIdSchema

    def _execute(self, element_id: str, text: str) -> str:
        
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
        browser_wrapper.page.keyboard.type(text)

        return f"Typed '{text}' into element {element_id}"