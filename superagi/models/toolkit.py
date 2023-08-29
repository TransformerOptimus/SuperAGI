import json

import requests
from sqlalchemy import Column, Integer, String, Boolean

from superagi.models.base_model import DBBaseModel
from superagi.models.tool import Tool

marketplace_url = "https://app.superagi.com/api"
# marketplace_url = "http://localhost:8001"


class Toolkit(DBBaseModel):
    """
        ToolKit - Used to group tools together
        Attributes:
            id(int) : id of the tool kit
            name(str) : name of the tool kit
            description(str) : description of the tool kit
            show_toolkit(boolean) : indicates whether the tool kit should be shown based on the count of tools in the toolkit
            organisation_id(int) : org id of the to which tool config is related
            tool_code_link(str) : stores Github link for toolkit
    """
    __tablename__ = 'toolkits'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    show_toolkit = Column(Boolean)
    organisation_id = Column(Integer)
    tool_code_link = Column(String)

    def __repr__(self):
        return f"ToolKit(id={self.id}, name='{self.name}', description='{self.description}', " \
               f"show_toolkit={self.show_toolkit}," \
               f"organisation_id = {self.organisation_id}"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'show_toolkit': self.show_toolkit,
            'organisation_id': self.organisation_id
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            show_toolkit=data['show_toolkit'],
            organisation_id=data['organisation_id']
        )

    @staticmethod
    def add_or_update(session, name, description, show_toolkit, organisation_id, tool_code_link):
        # Check if the toolkit exists
        toolkit = session.query(Toolkit).filter(Toolkit.name == name,
                                                Toolkit.organisation_id == organisation_id).first()

        if toolkit:
            # Update the existing toolkit
            toolkit.name = name
            toolkit.description = description
            toolkit.show_toolkit = show_toolkit
            toolkit.organisation_id = organisation_id
            toolkit.tool_code_link = tool_code_link
        else:
            # Create a new toolkit
            toolkit = Toolkit(
                name=name,
                description=description,
                show_toolkit=show_toolkit,
                organisation_id=organisation_id,
                tool_code_link=tool_code_link
            )

            session.add(toolkit)

        session.commit()
        session.flush()
        return toolkit

    @classmethod
    def fetch_marketplace_list(cls, page):
        headers = {'Content-Type': 'application/json'}
        response = requests.get(
            marketplace_url + f"/toolkits/marketplace/list/{str(page)}",
            headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return []

    @classmethod
    def fetch_marketplace_detail(cls, search_str, toolkit_name):
        headers = {'Content-Type': 'application/json'}
        search_str = search_str.replace(' ', '%20')
        toolkit_name = toolkit_name.replace(' ', '%20')
        response = requests.get(
            marketplace_url + f"/toolkits/marketplace/{search_str}/{toolkit_name}",
            headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    @staticmethod
    def get_toolkit_from_name(session, toolkit_name, organisation):
        toolkit = session.query(Toolkit).filter_by(name=toolkit_name, organisation_id=organisation.id).first()
        if toolkit:
            return toolkit
        return None

    @classmethod
    def get_toolkit_installed_details(cls, session, marketplace_toolkits, organisation):
        installed_toolkits = session.query(Toolkit).filter(Toolkit.organisation_id == organisation.id).all()
        for toolkit in marketplace_toolkits:
            if toolkit['name'] in [installed_toolkit.name for installed_toolkit in installed_toolkits]:
                toolkit["is_installed"] = True
            else:
                toolkit["is_installed"] = False
        return marketplace_toolkits

    @classmethod
    def fetch_tool_ids_from_toolkit(cls, session, toolkit_ids):
        agent_toolkit_tools = []
        for toolkit_id in toolkit_ids:
            toolkit_tools = session.query(Tool).filter(Tool.toolkit_id == toolkit_id).all()
            for tool in toolkit_tools:
                tool = session.query(Tool).filter(Tool.id == tool.id).first()
                if tool is not None:
                    agent_toolkit_tools.append(tool.id)
        return agent_toolkit_tools

    @classmethod
    def get_tool_and_toolkit_arr(cls, session, organisation_id :int,agent_config_tools_arr: list):
        from superagi.models.tool import Tool
        toolkits_arr= set()
        tools_arr= set()
        for tool_obj in agent_config_tools_arr:
            toolkit=session.query(Toolkit).filter(Toolkit.name == tool_obj["name"].strip(), Toolkit.organisation_id == organisation_id).first()
            if toolkit is None:
                raise Exception("One or more of the Tool(s)/Toolkit(s) does not exist.")
            toolkits_arr.add(toolkit.id)
            if tool_obj.get("tools"):
                for tool_name_str in tool_obj["tools"]:
                    tool_db_obj = session.query(Tool).filter(Tool.name == tool_name_str.strip(),
                                                             Tool.toolkit_id == toolkit.id).first()
                    if tool_db_obj is None:
                            raise Exception("One or more of the Tool(s)/Toolkit(s) does not exist.")

                    tools_arr.add(tool_db_obj.id)
            else:
                tools=Tool.get_toolkit_tools(session, toolkit.id)
                for tool_db_obj in tools:
                    tools_arr.add(tool_db_obj.id)
        return list(tools_arr)
