from typing import Type, Optional
from pydantic import Field, BaseModel
from superagi.tools.base_tool import BaseTool
import requests

class TelegramMessageSchema(BaseModel):
    chat_id: str = Field(
        ...,
        description="Unique identifier for the target chat or username of the target channel (in the format @channelusername)"
    )
    message: str = Field(
        ...,
        description="Text of the message to be sent"
    )

class TelegramSendMessageTool(BaseTool):
    """
    Telegram Message Tool
    
    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name = "SendTelegramMessage"
    description = "Send text message in Telegram"
    args_schema: Type[TelegramMessageSchema] = TelegramMessageSchema

    def _execute(self, chat_id: str, message: str):
        """
        Execute the Telegram Message Tool.
        
        Args:
            chat_id : The chat id.
            message : The message to be sent.
        
        Returns:
            success message if message is sent successfully or failure message if message sending fails.
        """
        telegram_bot_token = self.get_tool_config("TELEGRAM_BOT_TOKEN")
        if not telegram_bot_token:
            return "Error: TELEGRAM_BOT_TOKEN is not set in the configuration."

        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return f"Message sent to {chat_id} successfully"
            else:
                return f"Message sending failed. Status Code: {response.status_code}. Response: {response.text}"
        except Exception as e:
            return f"Error sending message: {e}"
