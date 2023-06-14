from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from superagi.helper.browser_wrapper import browser_wrapper

from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

class ScrollDirectionEnum(str):
    UP = "up"
    DOWN = "down"

class ScrollSchema(BaseModel):
    direction: ScrollDirectionEnum = Field(
        ..., 
        description="The scroll direction - 'up' or 'down'.",
        )

class ScrollTool(BaseTool):
    name = "PlaywrightScroll"
    description = "A tool for scrolling the webpage up or down using Playwright."
    args_schema: Type[ScrollSchema] = ScrollSchema

    def _execute(self, direction: ScrollDirectionEnum) -> str:
        page = browser_wrapper.page

        if direction == ScrollDirectionEnum.UP:
            page.evaluate(
                "(document.scrollingElement || document.body).scrollTop = (document.scrollingElement || document.body).scrollTop - window.innerHeight;"
            )
            return "Scrolled up!"
        elif direction == ScrollDirectionEnum.DOWN:
            page.evaluate(
                "(document.scrollingElement || document.body).scrollTop = (document.scrollingElement || document.body).scrollTop + window.innerHeight;"
            )
            return "Scrolled down!"

        return "Invalid scroll direction."