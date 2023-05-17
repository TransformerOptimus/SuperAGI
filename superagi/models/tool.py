# from sqlalchemy import Column, Integer, String,ForeignKey
# from base_model import DBBaseModel
# from sqlalchemy.orm import relationship
# from agent import Agent


# class Tool(DBBaseModel):
#     __tablename__ = 'tools'

#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     description = Column(String)
#     agent_id = Column(Integer,ForeignKey(Agent.id))
#     agent = relationship(Agent)
    

#     def __repr__(self):
#         return f"Tool(id={self.id}, name='{self.name}')"

