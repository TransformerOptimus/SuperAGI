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
        description = "Text Message to be sent to a person or a group or people"
    )

class SlackMessageTool(BaseTool):
    '''
    This Tool works for both Individual and Group messages
        - Individual Texting - Provide user-id 
        - Group Texting - Provide group-id
    '''
    name = "SendSlackMessage"
    description = "Send text message in Slack"
    args_schema: Type[SlackMessageSchema] = SlackMessageSchema
    
    def _execute(self, channel: str, message: str):
        slack = self.build_slack_web_client()
        response = slack.chat_postMessage(channel=channel, text=message)
        
        if response['ok']:
            return f'Message sent to {channel} Successfully'
        else:
            return 'Message sending failed!'

    @classmethod
    def build_slack_web_client(cls):
        slack_bot_token = get_config("SLACK_BOT_TOKEN")
        return WebClient(token=slack_bot_token)
