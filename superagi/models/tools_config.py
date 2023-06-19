from sqlalchemy import Column, Integer, String
from superagi.models.base_model import DBBaseModel


# from pydantic import BaseModel

class ToolConfig(DBBaseModel):
    """
    Model representing a tool configuration.

    Attributes:
        id (Integer): The primary key of the tool configuration.
        name (String): The name of the tool configuration.
        key (String): The key of the tool configuration.
        value (String): The value of the tool configuration.
        agent_id (Integer): The ID of the associated agent.
    """

    __tablename__ = 'tool_configs'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    key = Column(String)
    value = Column(String)
    agent_id = Column(Integer)

    def __repr__(self):
        """
        Returns a string representation of the ToolConfig object.

        Returns:
            str: String representation of the ToolConfig object.
        """

        return f"ToolConfig(id={self.id}, name='{self.name}', key='{self.key}', value='{self.value}', agent_id={self.agent_id})"
