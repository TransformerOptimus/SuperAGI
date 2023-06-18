from sqlalchemy import Column, DateTime, INTEGER
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class DBBaseModel(Base):
    """
    Base model for SQLAlchemy models.

    Attributes:
        created_at (DateTime): The timestamp indicating the creation time of the record.
        updated_at (DateTime): The timestamp indicating the last update time of the record.
    """

    __abstract__ = True
    # id  = Column(INTEGER,primary_key=True,autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
