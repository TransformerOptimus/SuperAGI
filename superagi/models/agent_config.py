from fastapi import HTTPException
from sqlalchemy import Column, Integer, Text, String

from superagi.config.config import get_config
from superagi.helper.encyption_helper import decrypt_data
from superagi.models.base_model import DBBaseModel
from superagi.models.configuration import Configuration
from superagi.types.model_source_types import ModelSourceType
from superagi.models.tool import Tool


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
