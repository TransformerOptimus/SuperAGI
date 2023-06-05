from sqlalchemy import Column, Integer, String,Float
from superagi.models.base_model import DBBaseModel
from sqlalchemy.orm import sessionmaker

class Resource(DBBaseModel):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    storage_type = Column(String) #FILESERVER,S3
    path = Column(String) #need for S3
    size = Column(Integer)
    type = Column(String) # application/pdf etc
    channel = Column(String) #INPUT,OUTPUT
    agent_id = Column(Integer)

    def __repr__(self):
        return f"Resource(id={self.id}, name='{self.name}', storage_type='{self.storage_type}', path='{self.path}, size='{self.size}', type='{self.type}', channel={self.channel}, agent_id={self.agent_id})"
