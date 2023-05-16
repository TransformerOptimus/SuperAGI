from sqlalchemy import Column, Integer, String
from base_model import BaseModel
from sqlalchemy.orm import relationship


class Tool(BaseModel):
    __tablename__ = 'tools'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __repr__(self):
        return f"Tool(id={self.id}, name='{self.name}')"

