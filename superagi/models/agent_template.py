import json

from sqlalchemy import Column, Integer, String, Text

from superagi.models.agent_template_step import AgentTemplateStep
from superagi.models.base_model import DBBaseModel


class AgentTemplate(DBBaseModel):
    __tablename__ = 'agent_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)

    def __repr__(self):
        return f"AgentTemplate(id={self.id}, name='{self.name}', " \
               f"description='{self.description}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description']
        )

    @classmethod
    def fetch_trigger_step_id(cls, session, template_id):
        trigger_step = session.query(AgentTemplateStep).filter(AgentTemplateStep.agent_template_id == template_id,
                                                AgentTemplateStep.step_type == 'TRIGGER').first()
        return trigger_step.id