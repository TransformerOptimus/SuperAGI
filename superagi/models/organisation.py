from sqlalchemy import Column, Integer, String
from superagi.models.base_model import DBBaseModel
from sqlalchemy.orm import relationship


class Organisation(DBBaseModel):
    __tablename__ = 'organisations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __repr__(self):
        return f"Organisation(id={self.id}, name='{self.name}')"
