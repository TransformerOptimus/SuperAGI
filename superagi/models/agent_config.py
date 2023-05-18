from sqlalchemy import Column, Integer, String, ForeignKey
from base_model import DBBaseModel
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from agent import Agent
# from llm import LLM
# from tool import Tool
from sqlalchemy.dialects.postgresql import ARRAY


class AgentConfiguration(DBBaseModel):
    __tablename__ = 'agent_configurations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    goal = Column(String)
    agent_id = Column(Integer, ForeignKey(Agent.id))
    agent = relationship(Agent)
    constraints = Column(String)
    base_prompt = Column(String)
    response = Column(JSON)
    # tool_id = Column(Integer,ForeignKey(Tool.id))
    # tools = relationship(Tool)
    tools = Column(ARRAY(String))
    exit_condition = Column(String)
    # llm_id = Column(Integer, ForeignKey())
    # llm = relationship(LLM)
    llms = Column(ARRAY(String))

    def __repr__(self):
        return f"AgentConfiguration(id={self.id}, goal={self.goal}, agent_id={self.agent_id}, constraints={self.constraints}, base_prompt={self.base_prompt}, response={self.response}, tools={self.tools}, exit_condition={self.exit_condition}, llms={self.llms})"
