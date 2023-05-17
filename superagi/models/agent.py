from sqlalchemy import Column, Integer, String,ForeignKey
from base_model import DBBaseModel
from project import Project

class Agent(DBBaseModel):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String)
    project_id = Column(Integer,ForeignKey(Project.id))
    description = Column(String)

    def __repr__(self):
        return f"Agent(id={self.id}, name='{self.name}', project_id={self.project_id}, " \
               f"description='{self.description}')"