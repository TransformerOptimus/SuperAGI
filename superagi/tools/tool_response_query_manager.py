from sqlalchemy.orm import Session

from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.vector_store.base import VectorStore

class ToolResponseQueryManager:
    def __init__(self, session: Session, agent_execution_id: int,memory:VectorStore):
        self.session = session
        self.agent_execution_id = agent_execution_id
        self.memory=memory

    def get_last_response(self, tool_name: str = None):
        return AgentExecutionFeed.get_last_tool_response(self.session, self.agent_execution_id, tool_name)
    
    def get_relevant_response(self, query: str,metadata:dict, top_k: int = 5):
        if self.memory is None:
            return ""
        documents = self.memory.get_matching_text(query, metadata=metadata)
        relevant_responses = ""
        for document in documents["documents"]:
            relevant_responses += document.text_content
        return relevant_responses
