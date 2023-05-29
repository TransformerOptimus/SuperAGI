from sqlalchemy import Column, Integer, String
from superagi.models.base_model import DBBaseModel
# from pydantic import BaseModel

class ToolConfig(DBBaseModel):
    __tablename__ = 'tool_configs'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    key = Column(String)
    value = Column(String)
    agent_id = Column(Integer)

    def __repr__(self):
        return f"ToolConfig(id={self.id}, name='{self.name}', key='{self.key}', value='{self.value}', agent_id={self.agent_id})"
