from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from superagi.tools.telegram.telegram_send_message import TelegramSendMessageTool
from superagi.types.key_type import ToolConfigKeyType

class TelegramToolkit(BaseToolkit, ABC):
    name: str = "Telegram Toolkit"
    description: str = "Toolkit containing tools for Telegram integration"

    def get_tools(self) -> List[BaseTool]:
        return [
            TelegramSendMessageTool(),
        ]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
            ToolConfiguration(key="TELEGRAM_BOT_TOKEN", key_type=ToolConfigKeyType.STRING, is_required=True, is_secret=True)
        ]
