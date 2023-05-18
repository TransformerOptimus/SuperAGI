from sqlalchemy import Column, Integer, Enum, Float
from superagi.models.base_model import DBBaseModel
from sqlalchemy.orm import sessionmaker

class Budget(DBBaseModel):
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    budget = Column(Float)
    cycle = Column(Enum('DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY',name='budget_cycle_enum'))

    def __repr__(self):
        return f"OrganisationUser(id={self.id}, name='{self.name}', " \
            f"project_id={self.project_id}, description='{self.description}')"