from sqlalchemy import Column, Integer, String
from superagi.models.base_model import DBBaseModel
# from pydantic import BaseModel

class User(DBBaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    organisation_id = Column(Integer)


    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}', email='{self.email}', password='{self.password}', organisation_id={self.organisation_id})"
