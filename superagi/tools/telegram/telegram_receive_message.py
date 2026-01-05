from typing import Type, Optional, List
from pydantic import Field, BaseModel
from superagi.tools.base_tool import BaseTool
import requests

class TelegramReceiveMessageSchema(BaseModel):
    limit: int = Field(
        10,
        description="Number of messages to retrieve (default 10)"
    )

class TelegramReceiveMessageTool(BaseTool):
    """
    Telegram Receive Message Tool
    
    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name = "ReadTelegramMessages"
    description = "Read recent messages from the bot's chat history"
    args_schema: Type[TelegramReceiveMessageSchema] = TelegramReceiveMessageSchema

    def _execute(self, limit: int = 10):
        """
        Execute the Telegram Receive Message Tool.
        
        Args:
           limit: Number of messages to retrieve.
        
        Returns:
            Recent messages or failure message.
        """
        telegram_bot_token = self.get_tool_config("TELEGRAM_BOT_TOKEN")
        if not telegram_bot_token:
            return "Error: TELEGRAM_BOT_TOKEN is not set in the configuration."

        url = f"https://api.telegram.org/bot{telegram_bot_token}/getUpdates"
        params = {
            "limit": limit,
            "offset": -limit  # Get the last N messages
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if not data.get("ok"):
                    return f"Error from Telegram: {data.get('description')}"
                
                messages = []
                for result in data.get("result", []):
                    message = result.get("message", {})
                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text")
                    sender = message.get("from", {}).get("username", "Unknown")
                    if text and chat_id:
                        messages.append(f"[{chat_id}] {sender}: {text}")
                
                if not messages:
                    return "No new text messages found."
                
                return "\n".join(messages)
            else:
                return f"Failed to retrieve messages. Status Code: {response.status_code}. Response: {response.text}"
        except Exception as e:
            return f"Error retrieving messages: {e}"
