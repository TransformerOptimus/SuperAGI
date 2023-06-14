from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from superagi.helper.browser_wrapper import browser_wrapper

from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
class EnterSchema(BaseModel):
    pass


class EnterTool(BaseTool):
    name = "PlaywrightEnter"
    description = "A tool for pressing the Enter key using Playwright."
    args_schema: Type[EnterSchema] = EnterSchema

    def _execute(self) -> str:
        page = browser_wrapper.page

        page.keyboard.press("Enter")
        return "Pressed enter!"