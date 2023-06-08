from typing import Any, Type
from pydantic import BaseModel
from superagi.config.config import get_config
from superagi.tools.base_tool import BaseTool

from slack_sdk import WebClient


class SlackTool(BaseTool):
    name = "SlackTool"
    description = "Base method for slack tool"
    args_schema: Type[BaseModel] = BaseModel
    @classmethod
    def build_slack_web_client(cls):
        slack_bot_token = get_config("SLACK_BOT_TOKEN")
        return WebClient(token=slack_bot_token)
    
    def _execute(self, *args: Any, **kwargs: Any):
        return super()._execute(*args, **kwargs)
