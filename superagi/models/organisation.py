from sqlalchemy import Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
from base_model import BaseModel
from sqlalchemy.orm import relationship


# Base = declarative_base()

class Organisation(BaseModel):
    __tablename__ = 'organisations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    # projects = relationship('Project',backref='organistaions')

    def __repr__(self):
        return f"Organisation(id={self.id}, name='{self.name}')"

