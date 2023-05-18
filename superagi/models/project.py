from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from base_model import DBBaseModel
from organisation import Organisation


class Project(DBBaseModel):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    # organisation_id = Column(Integer,ForeignKey('organisations.id'))
    organisation_id = Column(Integer,ForeignKey(Organisation.id))
    description = Column(String)
    organisations = relationship(Organisation)

    def __repr__(self):
        return f"Project(id={self.id}, name='{self.name}')"


    # organisation = relationship("Organisation", uselist=False, back_populates="projects")
