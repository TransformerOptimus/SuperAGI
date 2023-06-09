from __future__ import annotations

import json

from sqlalchemy import Column, Integer, String

import superagi.models
#from superagi.models import AgentConfiguration
from superagi.models.base_model import DBBaseModel



class Agent(DBBaseModel):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    project_id = Column(Integer)
    description = Column(String)
    agent_template_id = Column(Integer)

    def __repr__(self):
        return f"Agent(id={self.id}, name='{self.name}', project_id={self.project_id}, " \
               f"description='{self.description}', agent_template_id={self.agent_template_id})"

    @classmethod
    def fetch_configuration(cls, session, agent_id: int):
        agent = session.query(Agent).filter_by(id=agent_id).first()
        agent_configurations = session.query(superagi.models.agent_config.AgentConfiguration).filter_by(agent_id=agent_id).all()
        # print("Configuration ", agent_configurations)
        parsed_config = {
            "agent_id": agent.id,
            "name": agent.name,
            "project_id": agent.project_id,
            "description": agent.description,
            "goal": [],
            "agent_type": None,
            "constraints": [],
            "tools": [],
            "exit": None,
            "iteration_interval": None,
            "model": None,
            "permission_type": None,
            "LTM_DB": None,
            "memory_window": None,
            "max_iterations" : None
        }
        if not agent_configurations:
            return parsed_config
        for item in agent_configurations:
            key = item.key
            value = item.value

            if key == "name":
                parsed_config["name"] = value
            elif key == "project_id":
                parsed_config["project_id"] = int(value)
            elif key == "description":
                parsed_config["description"] = value
            elif key == "goal":
                parsed_config["goal"] = eval(value)
            elif key == "agent_type":
                parsed_config["agent_type"] = value
            elif key == "constraints":
                parsed_config["constraints"] = eval(value)
            elif key == "tools":
                parsed_config["tools"] = [int(x) for x in json.loads(value)]
            # elif key == "tools":
            # parsed_config["tools"] = eval(value)
            elif key == "exit":
                parsed_config["exit"] = value
            elif key == "iteration_interval":
                parsed_config["iteration_interval"] = int(value)
            elif key == "model":
                parsed_config["model"] = value
            elif key == "permission_type":
                parsed_config["permission_type"] = value
            elif key == "LTM_DB":
                parsed_config["LTM_DB"] = value
            elif key == "memory_window":
                parsed_config["memory_window"] = int(value)
            elif key == "max_iterations":
                parsed_config["max_iterations"] = int(value)
        return parsed_config
