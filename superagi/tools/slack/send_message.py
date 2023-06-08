from typing import Type

from pydantic import Field, BaseModel

from superagi.tools.slack.tool import SlackTool

class SlackMessageSchema(BaseModel):
    channel: str = Field(
        ...,
        description="Slack Channel/Group Name"
    )
    message: str = Field(
        ...,
        description = "Text Message to be sent to a person or a group or people"
    )

class SlackMessageTool(SlackTool):
    '''
    This Tool works for both Individual and Group messages
        - Individual Texting - Provide user-id 
        - Group Texting - Provide group-id
    '''
    name = "SlackMessage"
    description = "Send text message in Slack"
    args_schema: Type[SlackMessageSchema] = SlackMessageSchema
    
    def _execute(self, channel: str, message: str):
        slack = self.build_slack_web_client()
        response = slack.chat_postMessage(channel=channel, text=message)
        
        if response['ok']:
            return f'Message sent to {channel} Successfully'
        else:
            return 'Message sending failed!'
