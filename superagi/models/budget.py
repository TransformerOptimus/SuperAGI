from sqlalchemy import Column, Integer, String,Float
from superagi.models.base_model import DBBaseModel
from sqlalchemy.orm import sessionmaker

class Budget(DBBaseModel):
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    budget = Column(Float)
    cycle = Column(String)

    def __repr__(self):
        return (f"Budget(id={self.id}, budget={self.budget}, "
                f"cycle='{self.cycle}')")
