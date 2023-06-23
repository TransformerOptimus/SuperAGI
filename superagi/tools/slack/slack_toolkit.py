from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.slack.send_message import SlackMessageTool


class SlackToolkit(BaseToolkit, ABC):
    name: str = "Slack Toolkit"
    description: str = "Toolkit containing tools for Slack integration"

    def get_tools(self) -> List[BaseTool]:
        return [
            SlackMessageTool(),
        ]

    def get_env_keys(self) -> List[str]:
        return [
            "SLACK_BOT_TOKEN",
        ]
