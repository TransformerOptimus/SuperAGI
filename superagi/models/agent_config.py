from fastapi import HTTPException
from sqlalchemy import Column, Integer, Text, String
from typing import Union

from superagi.config.config import get_config
from superagi.helper.encyption_helper import decrypt_data
from superagi.models.base_model import DBBaseModel
from superagi.models.configuration import Configuration
from superagi.types.model_source_types import ModelSourceType
from superagi.models.tool import Tool
from superagi.controllers.types.agent_execution_config import AgentRunIn


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
    def update_agent_configurations_table(cls, session, agent_id: Union[int, None], updated_details: AgentRunIn):

        updated_details_dict = updated_details.dict()

        # Fetch existing 'toolkits' agent configuration for the given agent_id
        agent_toolkits_config = session.query(AgentConfiguration).filter(
            AgentConfiguration.agent_id == agent_id,
            AgentConfiguration.key == 'toolkits'
        ).first()

        if agent_toolkits_config:
            agent_toolkits_config.value = str(updated_details_dict['toolkits'])
        else:
            agent_toolkits_config = AgentConfiguration(
                agent_id=agent_id,
                key='toolkits',
                value=str(updated_details_dict['toolkits'])
            )
            session.add(agent_toolkits_config)
        
        #Fetch existing knowledge for the given agent id and update it accordingly
        knowledge_config = session.query(AgentConfiguration).filter(
            AgentConfiguration.agent_id == agent_id,
            AgentConfiguration.key == 'knowledge'
        ).first()

        if knowledge_config:
            knowledge_config.value = str(updated_details_dict['knowledge'])
        else:
            knowledge_config = AgentConfiguration(
                agent_id=agent_id,
                key='knowledge',
                value=str(updated_details_dict['knowledge'])
            )
            session.add(knowledge_config)
            
        # Fetch agent configurations
        agent_configs = session.query(AgentConfiguration).filter(AgentConfiguration.agent_id == agent_id).all()
        for agent_config in agent_configs:
            if agent_config.key in updated_details_dict:
                agent_config.value = str(updated_details_dict[agent_config.key])

        # Commit the changes to the database
        session.commit()

        return "Details updated successfully"
    
    @classmethod
    def get_model_api_key(cls, session, agent_id: int, model: str):
        """
        Get the model API key from the agent id.

        Args:
            session (Session): The database session
            agent_id (int): The agent identifier
            model (str): The model name

        Returns:
            str: The model API key.
        """
        config_model_source = Configuration.fetch_value_by_agent_id(session, agent_id,
                                                                    "model_source") or "OpenAi"
        selected_model_source = ModelSourceType.get_model_source_from_model(model)
        if selected_model_source.value == config_model_source:
            config_value = Configuration.fetch_value_by_agent_id(session, agent_id, "model_api_key")
            model_api_key = decrypt_data(config_value)
            return model_api_key

        if selected_model_source == ModelSourceType.GooglePalm:
            return get_config("PALM_API_KEY")

        if selected_model_source == ModelSourceType.Replicate:
            return get_config("REPLICATE_API_TOKEN")
        return get_config("OPENAI_API_KEY")
