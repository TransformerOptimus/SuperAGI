from sqlalchemy import Column, DateTime,INTEGER
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# class WrapperBaseMode(Base):

class DBBaseModel(Base):
    __abstract__ = True
    # id  = Column(INTEGER,primary_key=True,autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
