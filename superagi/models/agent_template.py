import json

import requests
from sqlalchemy import Column, Integer, String, Text

from superagi.models.base_model import DBBaseModel

marketplace_url = "https://app.superagi.com/api/"

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
