from pydantic import BaseModel
from superagi.tools.base_tool import BaseTool
from superagi.helper.browser_wrapper import browser_wrapper


class EnterSchema(BaseModel):
    pass


class EnterTool(BaseTool):
    name = "Enter"
    description = "A tool for pressing the Enter key using Playwright."
    args_schema = EnterSchema

    def _execute(self) -> str:
        page = browser_wrapper.page

        page.keyboard.press("Enter")
        return "Pressed enter!"