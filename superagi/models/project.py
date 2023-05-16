from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from base_model import BaseModel

Base = declarative_base()

class Project(BaseModel):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    organisation_id = Column(Integer,ForeignKey('projects.id'))

    project = relationship("project", uselist=False, back_populates="organisation")
