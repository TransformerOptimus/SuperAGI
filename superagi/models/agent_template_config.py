import json

from sqlalchemy import Column, Integer, String, Text

from superagi.models.agent_workflow_step import AgentWorkflowStep
from superagi.models.base_model import DBBaseModel


class AgentTemplateConfig(DBBaseModel):
    """Agent Template Configs are stored in this table. """
    __tablename__ = 'agent_template_configs'

    id = Column(Integer, primary_key=True)
    """Agent Template Config ID."""
    agent_template_id = Column(Integer)
    """Agent Template Id"""
    key = Column(String)
    """Agent Template Config Key"""
    value = Column(Text)
    """Agent Template Config Value"""


    def __repr__(self):
        return f"AgentTemplateConfig(id={self.id}, agent_template_id='{self.agent_template_id}', " \
               f"key='{self.key}', value='{self.value}')"

    def to_dict(self):
        return {
            'id': self.id,
            'agent_template_id': self.agent_template_id,
            'key': self.key,
            'value': self.value
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(
            id=data['id'],
            agent_template_id=data['agent_template_id'],
            key=data['key'],
            value=data['value']
        )

