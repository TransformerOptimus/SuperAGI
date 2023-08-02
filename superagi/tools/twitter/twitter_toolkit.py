from abc import ABC
from superagi.tools.base_tool import BaseToolkit, BaseTool, ToolConfiguration
from typing import Type, List
from superagi.tools.twitter.send_tweets import SendTweetsTool
from superagi.types.key_type import ToolConfigKeyType

class TwitterToolkit(BaseToolkit, ABC):
    name: str = "Twitter Toolkit"
    description: str = "Twitter Tool kit contains all tools related to Twitter"

    def get_tools(self) -> List[BaseTool]:
        return [SendTweetsTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
            ToolConfiguration(key="TWITTER_API_KEY", key_type=ToolConfigKeyType.STRING, is_required= True, is_secret = True),
            ToolConfiguration(key="TWITTER_API_SECRET", key_type=ToolConfigKeyType.STRING, is_required=True, is_secret= True)
        ]
