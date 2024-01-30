import os
import json

from langchain.schema import messages_from_dict, messages_to_dict
from langchain.memory import (
    ConversationBufferMemory,
    ChatMessageHistory,
)


class YeagerAIContext:
    """Context for the @yeager.ai agent."""

    def __init__(self, username: str, session_id: str, session_path: str):
        self.username = username
        self.session_id = session_id
        self.session_path = session_path

        self.session_message_history = ChatMessageHistory()
        self.chat_buffer_memory = ConversationBufferMemory(
            memory_key="chat_history", input_key="input"
        )

    def load_session_message_history(self):
        try:
            with open(os.path.join(self.session_path, "session_history.txt"), "r") as f:
                dicts = json.loads(f.read())
                self.session_message_history.messages = messages_from_dict(dicts)
        except FileNotFoundError:
            os.makedirs(self.session_path, exist_ok=True)
            with open(os.path.join(self.session_path, "session_history.txt"), "w") as f:
                f.close()

    def save_session_message_history(self):
        dicts = messages_to_dict(self.session_message_history.messages)
        with open(os.path.join(self.session_path, "session_history.txt"), "w") as f:
            f.write(json.dumps(dicts))
            f.close()

    def create_shadow_clones(self):
        self.load_session_message_history()
        self.chat_buffer_memory.chat_memory = self.session_message_history

    def dispell_shadow_clones(self):
        self.session_message_history = self.chat_buffer_memory.chat_memory
        self.save_session_message_history()
