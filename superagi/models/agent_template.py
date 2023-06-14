import json

import requests
from sqlalchemy import Column, Integer, String, Text

from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_template_config import AgentTemplateConfig
from superagi.models.agent_workflow import AgentWorkflow
from superagi.models.base_model import DBBaseModel
from superagi.models.tool import Tool

marketplace_url = "https://app.superagi.com/api/"
# marketplace_url = "http://localhost:8001/"


class AgentTemplate(DBBaseModel):
    """ AgentTemplate - used to store preconfigured agent templates"""
    __tablename__ = 'agent_templates'

    id = Column(Integer, primary_key=True)
    """ id - id of the agent template"""
    organisation_id = Column(Integer)
    """ organisation_id - org id of user or -1 if the template is public"""
    agent_workflow_id = Column(Integer)
    """ agent_workflow_id - id of the workflow that the agent will use"""
    name = Column(String)
    """ name - name of the agent template"""
    description = Column(Text)
    """ description - description of the agent template"""
    marketplace_template_id = Column(Integer)
    """ marketplace_template_id - id of the template in the marketplace"""

    def __repr__(self):
        return f"AgentTemplate(id={self.id}, name='{self.name}', " \
               f"description='{self.description}')"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description']
        )

    @classmethod
    def main_keys(cls):
        keys_to_fetch = ["goal", "agent_type", "constraints", "tools", "exit", "iteration_interval", "model",
                         "permission_type", "LTM_DB", "memory_window", "max_iterations"]
        return keys_to_fetch

    @classmethod
    def fetch_marketplace_list(cls, search_str, page):
        headers = {'Content-Type': 'application/json'}
        response = requests.get(
            marketplace_url + "agent_templates/marketplace/list?search=" + search_str + "&page=" + str(page),
            headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return []

    @classmethod
    def fetch_marketplace_detail(cls, agent_template_id):
        headers = {'Content-Type': 'application/json'}
        response = requests.get(
            marketplace_url + "agent_templates/marketplace/template_details/" + str(agent_template_id),
            headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {}

    @classmethod
    def clone_agent_template_from_marketplace(cls, db, organisation_id: int, agent_template_id: int):
        """ Clones an agent template from marketplace and saves it in the database"""
        agent_template = AgentTemplate.fetch_marketplace_detail(agent_template_id)
        agent_workflow = db.session.query(AgentWorkflow).filter(
            AgentWorkflow.name == agent_template["agent_workflow_name"]).first()
        template = AgentTemplate(organisation_id=organisation_id, agent_workflow_id=agent_workflow.id,
                                 name=agent_template["name"], description=agent_template["description"],
                                 marketplace_template_id=agent_template["id"])
        db.session.add(template)
        db.session.commit()
        db.session.flush()

        agent_configurations = []
        for key, value in agent_template["configs"].items():
            # Converting tool names to ids and saving it in agent configuration
            agent_configurations.append(
                AgentTemplateConfig(agent_template_id=template.id, key=key, value=str(value["value"])))

        db.session.add_all(agent_configurations)
        db.session.commit()
        db.session.flush()
        return template

    @classmethod
    def eval_agent_config(cls, key, value):
        if key in ["name", "description", "agent_type", "exit", "model", "permission_type", "LTM_DB"]:
            return value
        elif key in ["project_id", "memory_window", "max_iterations", "iteration_interval"]:
            return int(value)
        elif key == "goal" or key == "constraints":
            return eval(value)
        elif key == "tools":
            return [str(x) for x in eval(value)]