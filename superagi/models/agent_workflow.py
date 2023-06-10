import json

from sqlalchemy import Column, Integer, String, Text

from superagi.models.agent_workflow_step import AgentWorkflowStep
from superagi.models.base_model import DBBaseModel


class AgentWorkflow(DBBaseModel):
    __tablename__ = 'agent_workflows'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)

    def __repr__(self):
        return f"AgentWorkflow(id={self.id}, name='{self.name}', " \
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
    def fetch_trigger_step_id(cls, session, workflow_id):
        trigger_step = session.query(AgentWorkflowStep).filter(AgentWorkflowStep.agent_workflow_id == workflow_id,
                                                               AgentWorkflowStep.step_type == 'TRIGGER').first()
        return trigger_step.id