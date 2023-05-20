from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from superagi.models.base_model import DBBaseModel
from superagi.models.organisation import Organisation


class Project(DBBaseModel):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    organisation_id = Column(Integer)
    description = Column(String)

    def __repr__(self):
        return f"Project(id={self.id}, name='{self.name}')"


