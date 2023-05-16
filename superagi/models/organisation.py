from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from base_model import BaseModel

Base = declarative_base()

class Organisation(BaseModel):
    __tablename__ = 'Organistaions'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    



