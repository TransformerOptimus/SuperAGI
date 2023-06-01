import json

from sqlalchemy import Column, Integer, String, Text, Boolean

from superagi.models.base_model import DBBaseModel


class AgentTemplateStep(DBBaseModel):
    __tablename__ = 'agent_template_steps'

    id = Column(Integer, primary_key=True)
    agent_template_id = Column(Integer)
    prompt = Column(Text)
    variables = Column(Text)
    output_type = Column(String)
    step_type = Column(String) # TRIGGER, NORMAL
    next_step_id = Column(Integer)
    history_enabled = Column(Boolean)
    completion_prompt = Column(Text)

    def __repr__(self):
        return f"AgentStep(id={self.id}, status='{self.next_step_id}', " \
               f"prompt='{self.prompt}', agent_id={self.agent_id})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'next_step_id': self.next_step_id,
            'agent_id': self.agent_id,
            'prompt': self.prompt
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(
            id=data['id'],
            prompt=data['prompt'],
            agent_id=data['agent_id'],
            next_step_id=data['next_step_id']
        )

