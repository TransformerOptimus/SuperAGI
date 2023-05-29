from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from superagi.helper.slack_helper import SlackHelper
from superagi.config.config import get_config
import os
import re

class SlackToolSchema(BaseModel):
    channel_name: str = Field(..., description="The name of the channel to read messages from.")

class SlackTool(BaseTool):
    name = "Slack Tool"
    description = (
        "A tool for reading unread messages in a Slack channel."
    )
    args_schema: Type[SlackToolSchema] = SlackToolSchema

    def _execute(self, channel_name: str) -> tuple:
        slack_bot_token = get_config("SLACK_BOT_TOKEN")
        slack_helper = SlackHelper(slack_bot_token)

        channel_id = None
        for channel in slack_helper.get_channels():
            if channel["name"] == channel_name:
                channel_id = channel["id"]
                break

        if not channel_id:
            raise ValueError(f"Channel {channel_name} not found")

        unread_messages = slack_helper.get_unread_messages(channel_id)

        return {"unread_messages": unread_messages}