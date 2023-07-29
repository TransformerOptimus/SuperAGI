from sqlalchemy.orm import Session

from superagi.models.agent_execution_feed import AgentExecutionFeed


class ToolResponseQueryManager:
    def __init__(self, session: Session, agent_execution_id: int):
        self.session = session
        self.agent_execution_id = agent_execution_id

    def get_last_response(self, tool_name: str = None):
        return AgentExecutionFeed.get_last_tool_response(self.session, self.agent_execution_id, tool_name)
