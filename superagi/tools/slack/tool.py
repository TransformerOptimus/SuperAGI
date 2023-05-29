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
    
    def generate_userid_cum_name_dict(self):
        slack = self.build_slack_web_client()
        response_conversations_list, response_users_list = slack.conversations_list(), slack.users_list()
        slack_id_name_dict = {'channels':{}, 'users': {}}
        if response_conversations_list['ok']:
            channels = response_conversations_list['channels']
            for channel in channels:
                slack_id_name_dict['channels'][channel['id']] = channel['name']
                
        if response_users_list['ok']:
            members = response_users_list['members']
            for member in members:
                slack_id_name_dict['users'][member['id']] = member['name']
        
        return slack_id_name_dict
    
    def _execute(self, *args: Any, **kwargs: Any):
        return super()._execute(*args, **kwargs)
