from sqlalchemy import Column, Integer, String
from superagi.models.base_model import DBBaseModel
from superagi.models.project import Project
from sqlalchemy.orm import relationship

class Agent(DBBaseModel):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String)
    project_id = Column(Integer)
    description = Column(String)

    def __repr__(self):
        return f"Agent(id={self.id}, name='{self.name}', project_id={self.project_id}, " \
               f"description='{self.description}')"