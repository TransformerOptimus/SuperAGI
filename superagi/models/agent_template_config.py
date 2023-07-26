import json

from sqlalchemy import Column, Integer, String, Text

from superagi.models.base_model import DBBaseModel


class AgentTemplateConfig(DBBaseModel):
    """
    Agent template related configurations like goals, instructions, constraints and tools are stored here

    Attributes:
        id (int): The unique identifier of the agent template config.
        agent_template_id (int): The identifier of the associated agent template.
        key (str): The key of the configuration setting.
        value (str): The value of the configuration setting.
    """

    __tablename__ = 'agent_template_configs'

    id = Column(Integer, primary_key=True)
    agent_template_id = Column(Integer)
    key = Column(String)
    value = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the AgentTemplateConfig object.

        Returns:
            str: String representation of the AgentTemplateConfig.
        """

        return f"AgentTemplateConfig(id={self.id}, agent_template_id='{self.agent_template_id}', " \
               f"key='{self.key}', value='{self.value}')"

    def to_dict(self):
        """
        Converts the AgentTemplateConfig object to a dictionary.

        Returns:
            dict: Dictionary representation of the AgentTemplateConfig.
        """

        return {
            'id': self.id,
            'agent_template_id': self.agent_template_id,
            'key': self.key,
            'value': self.value
        }

    def to_json(self):
        """
        Converts the AgentTemplateConfig object to a JSON string.

        Returns:
            str: JSON string representation of the AgentTemplateConfig.
        """

        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        """
        Creates an AgentTemplateConfig object from a JSON string.

        Args:
            json_data (str): JSON string representing the AgentTemplateConfig.

        Returns:
            AgentTemplateConfig: AgentTemplateConfig object created from the JSON string.
        """

        data = json.loads(json_data)
        return cls(
            id=data['id'],
            agent_template_id=data['agent_template_id'],
            key=data['key'],
            value=data['value']
        )
