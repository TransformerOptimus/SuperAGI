from fastapi import HTTPException
from sqlalchemy import Column, Integer, Text, String
from sqlalchemy.orm import sessionmaker

from superagi.models.base_model import DBBaseModel
from superagi.models.db import connect_db
from superagi.models.tool import Tool

engine = connect_db()
Session = sessionmaker(bind=engine)


class AgentConfiguration(DBBaseModel):
    """
    Agent related configurations like goals, instructions, constraints and tools are stored here

    Attributes:
        id (int): The unique identifier of the agent configuration.
        agent_id (int): The identifier of the associated agent.
        key (str): The key of the configuration setting.
        value (str): The value of the configuration setting.
    """

    __tablename__ = 'agent_configurations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer)
    key = Column(String)
    value = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the Agent Configuration object.

        Returns:
            str: String representation of the Agent Configuration.

        """
        return f"AgentConfiguration(id={self.id}, key={self.key}, value={self.value})"

    @classmethod
    def get_tools_from_agent_config(cls, session, agent_with_config):
        agent_toolkit_tools = []
        for toolkit_id in agent_with_config.toolkits:
            toolkit_tools = session.query(Tool).filter(Tool.toolkit_id == toolkit_id).all()
            for tool in toolkit_tools:
                tool = session.query(Tool).filter(Tool.id == tool.id).first()
                if tool is None:
                    # Tool does not exist, throw 404
                    raise HTTPException(status_code=404, detail=f"Tool does not exist. 404 Not Found.")
                else:
                    agent_toolkit_tools.append(tool.id)
        return agent_toolkit_tools

    @classmethod
    def update_agent_config_key(cls, agent_id, key, value):
        """
        Updates the agent configuration for the given agent id.

        Args:
            agent_id (int): The identifier of the agent.
            key (str): The key of the configuration setting.
            value (str): The value of the configuration setting.

        Returns:
            AgentConfiguration: The updated agent configuration.
        """
        session = Session()
        agent_config = session.query(cls).filter(cls.agent_id == agent_id).filter(cls.key == key).first()
        if agent_config is None:
            agent_config = AgentConfiguration(agent_id=agent_id, key=key, value=value)
            session.add(agent_config)
        else:
            agent_config.value = value
        session.commit()
        session.close()
