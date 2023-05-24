from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from superagi.models.base_model import DBBaseModel
from superagi.models.organisation import Organisation


# from pydantic import BaseModel

class User(DBBaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    organisation_id = Column(Integer, ForeignKey('organisations.id'))
    organisation = relationship(Organisation)

    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}', email='{self.email}', password='{self.password}')"
