from sqlalchemy import Column, Integer, String
from superagi.models.base_model import DBBaseModel

class CallLogs(DBBaseModel):
    """
    Represents a Model record in the database

    Attributes:
        id (Integer): The unique identifier of the event.
        agent_execution_name (String): The name of the agent_execution.
        agent_id (Integer): The unique id of the model_provider from the models_config table.
        tokens_consumed (Integer): The number of tokens for a call.
        tool_used (String): The tool_used for the call.
        model (String): The model used for the Agent call.
        org_id (Integer): The ID of the organisation.
    """

    __tablename__ = 'call_logs'

    id = Column(Integer, primary_key=True)
    agent_execution_name = Column(String, nullable=False)
    agent_id = Column(Integer, nullable=False)
    tokens_consumed = Column(Integer, nullable=False)
    tool_used = Column(String, nullable=False)
    model = Column(String, nullable=True)
    org_id = Column(Integer, nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the CallLogs instance.
        """
        return f"CallLogs(id={self.id}, agent_execution_name={self.agent_execution_name}, " \
               f"agent_id={self.agent_id}, tokens_consumed={self.tokens_consumed}, " \
               f"tool_used={self.tool_used}, " \
               f"model={self.model}, " \
               f"org_id={self.org_id})"