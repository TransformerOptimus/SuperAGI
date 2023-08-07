from sqlalchemy import Column, Integer, Text, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from superagi.models.base_model import DBBaseModel
from superagi.models.agent_execution import AgentExecution


class AgentExecutionPermission(DBBaseModel):
    """
    Agent Execution Permissions at each step to be approved or rejected by the user.

    Attributes:
        id (Integer): The primary key of the agent execution permission record.
        agent_execution_id (Integer): The ID of the agent execution this permission record is associated with.
        agent_id (Integer): The ID of the agent this permission record is associated with.
        status (String): The status of the agent execution permission, APPROVED, REJECTED, or PENDING.
        tool_name (String): The name of the tool or service that requires the permission.
        user_feedback (Text): Any feedback provided by the user regarding the agent execution permission.
        assistant_reply (Text): The reply or message sent back to the user by the assistant.

    Methods:
        __repr__: Returns a string representation of the AgentExecutionPermission instance.
    """
    __tablename__ = 'agent_execution_permissions'

    id = Column(Integer, primary_key=True)
    agent_execution_id = Column(Integer)
    agent_id = Column(Integer)
    status = Column(String)
    tool_name = Column(String)
    user_feedback = Column(Text)
    question = Column(Text)
    assistant_reply = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the AgentExecutionPermission instance.
        """
        return f"AgentExecutionPermission(id={self.id}, " \
               f"agent_execution_id={self.agent_execution_id}, " \
               f"agent_id={self.agent_id}, " \
               f"status={self.status}, " \
               f"tool_name={self.tool_name}, " \
               f"question={self.question}, " \
               f"response={self.user_feedback})"
