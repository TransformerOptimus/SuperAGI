from sqlalchemy import Column, Integer, String, ForeignKey
from base_model import BaseModel
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from agent import Agent
from llm import LLM
from tool import Tool


class AgentConfiguration(BaseModel):
    __tablename__ = 'agent_configurations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    goal = Column(String)
    agent_id = Column(Integer, ForeignKey(Agent.id))
    agent = relationship(Agent)
    constraints = Column(String)
    base_prompt = Column(String)
    response = Column(JSON)
    tool_id = Column(Integer,ForeignKey(Tool.id))
    tools = relationship(Tool)
    exit_condition = Column(String)
    llm_id = Column(Integer, ForeignKey())
    llm = relationship(LLM)

    def __repr__(self):
        return f"LLM(id={self.id}, company='{self.company}', model_name='{self.model_name}', " \
               f"max_tokens={self.max_tokens}, temperature={self.temperature}, " \
               f"top_p={self.top_p}, prompt='{self.prompt}', " \
               f"number_of_results={self.number_of_results}, " \
               f"frequency_penalty={self.frequency_penalty}, " \
               f"presence_penalty={self.presence_penalty})"
