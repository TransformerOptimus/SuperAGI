from sqlalchemy import Column, Integer, Enum, Float
from base_model import BaseModel
from db import engine,connectDB
from sqlalchemy.orm import sessionmaker

class User(BaseModel):
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    budget = Column(Float)
    cycle = Column(Enum('DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY'))

    def __repr__(self):
        return f"OrganisationUser(id={self.id}, name='{self.name}', " \
            f"project_id={self.project_id}, description='{self.description}')"