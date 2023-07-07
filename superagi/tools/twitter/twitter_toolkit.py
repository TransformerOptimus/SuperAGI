from abc import ABC
from superagi.tools.base_tool import BaseToolkit, BaseTool
from typing import Type, List
from superagi.tools.twitter.send_tweets import SendTweetsTool


class TwitterToolkit(BaseToolkit, ABC):
    name: str = "Twitter Toolkit"
    description: str = "Twitter Tool kit contains all tools related to Twitter"

    def get_tools(self) -> List[BaseTool]:
        return [SendTweetsTool()]

    def get_env_keys(self) -> List[str]:
        return ["TWITTER_API_KEY", "TWITTER_API_SECRET"]
