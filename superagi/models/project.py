from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from superagi.models.base_model import DBBaseModel
from superagi.models.organisation import Organisation


class Project(DBBaseModel):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    organisation_id = Column(Integer, ForeignKey('organisations.id'))
    description = Column(String)
    organisation = relationship(Organisation)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"Project(id={self.id}, name='{self.name}')"


