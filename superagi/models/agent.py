from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from base_model import BaseModel

Base = declarative_base()

class Agent(BaseModel):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True)
    agent_name = Column(String)
    project_id = Column(Integer,ForeignKey('agent',ForeignKey()))
    description = Column(String)
