from typing import Type

from pydantic import Field, BaseModel

from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
from slack_sdk import WebClient


class SlackMessageSchema(BaseModel):
    channel: str = Field(
        ...,
        description="Slack Channel/Group Name"
    )
    message: str = Field(
        ...,
        description="Text Message to be sent to a person or a group or people"
    )


class SlackMessageTool(BaseTool):
    """
    Slack Message Tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.

    This Tool works for both Individual and Group messages
    - Individual Texting - Provide user-id
    - Group Texting - Provide group-id
    """
    name = "SendSlackMessage"
    description = "Send text message in Slack"
    args_schema: Type[SlackMessageSchema] = SlackMessageSchema

    def _execute(self, channel: str, message: str):
        """
        Execute the Slack Message Tool.

        Args:
            channel : The channel name.
            message : The message to be sent.

        Returns:
            success message if message is sent successfully or failure message if message sending fails.
        """
        slack = self.build_slack_web_client()
        response = slack.chat_postMessage(channel=channel, text=message)

        if response['ok']:
            return f'Message sent to {channel} Successfully'
        else:
            return 'Message sending failed!'

    def build_slack_web_client(self):
        slack_bot_token = self.get_tool_config("SLACK_BOT_TOKEN")
        return WebClient(token=slack_bot_token)
