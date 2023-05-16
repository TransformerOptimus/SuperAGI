from sqlalchemy import Column, Integer, String, ForeignKey
from base_model import BaseModel
from sqlalchemy.orm import relationship
from user import User
from organisation import Organisation

class OrganisationUser(BaseModel):
    __tablename__ = 'organisations'

    id = Column(Integer, primary_key=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey=User.id)
    organisation_id = Column(Integer,ForeignKey=Organisation)
    organisations = relationship(Organisation)
    user = relationship(User)

    def __repr__(self):
        return f"OrganisationUser(id={self.id}, user_id={self.user_id}, " \
               f"organisation_id={self.organisation_id}')"

    
