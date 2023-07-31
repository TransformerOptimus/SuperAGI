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
        
      
        documents = self.memory.get_matching_text(query, metadata=metadata)
        
        relevant_responses = ""
        for document in documents["documents"]:
            relevant_responses += document.text_content

        start_index = relevant_responses.find("Tool ThinkingTool returned:")
        if start_index != -1:
            start_index += len("Tool ThinkingTool returned:")
            extracted_string = relevant_responses[start_index:].strip()
            print("Extracted String:", extracted_string)    
            return extracted_string
        else:
            return ""
    