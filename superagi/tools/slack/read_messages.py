from typing import Any, Type

from pydantic import Field, BaseModel

from superagi.tools.slack.tool import SlackTool

class SlackReadMessageSchema(BaseModel):
    id: str = Field(
        ...,
        description="Slack User-Id/Group-Id"
    )
    
class SlackReadMessageTool(SlackTool):
    '''
    This Tool works for both Individual and Group messages
        - Individual Texting - Provide user-id 
        - Group Texting - Provide group-id
    
    NOTE: Makesure the Slack bot is a member of the group, if extracting the messages from a group
    '''
    name = "ReadSlackMessages"
    description = "Read the messages from individual or group chats in Slack"
    args_schema: Type[SlackReadMessageSchema] = SlackReadMessageSchema
    _config_for_conversational_data_extraction = ['type', 'subtype', 'user', 'text']
    
    def _execute(self, id: str):
        slack = self.build_slack_web_client()
        response = slack.conversations_history(channel=id)

        if not response['ok']:
            return "Failed to retrieve message history!"
        messages = response['messages']
        conversation = []
        
        for message in messages:
            message = {key: (message[key] if key in message else "") for key in self._config_for_conversational_data_extraction}
            conversation.append(message)
            
        return conversation