from sqlalchemy import Column, Integer, String,Text
from superagi.models.base_model import DBBaseModel


class Config(DBBaseModel):
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    organisation_id = Column(Integer)
    key = Column(String)
    value = Column(Text)

    def __repr__(self):
        return f"Config(id={self.id}, organisation_id={self.organisation_id}, key={self.key}, value={self.value})"
