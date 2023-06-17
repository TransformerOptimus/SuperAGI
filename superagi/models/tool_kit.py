import json
import requests
from sqlalchemy import Column, Integer, String, Boolean

from superagi.models.base_model import DBBaseModel

# marketplace_url = "https://app.superagi.com/api/"


marketplace_url = "http://localhost:8001"

class ToolKit(DBBaseModel):
    """ToolKit - used to store tool kits"""
    __tablename__ = 'tool_kits'

    id = Column(Integer, primary_key=True)
    """id - id of the tool kit"""
    name = Column(String)
    """name - name of the tool kit"""
    description = Column(String)
    """description - description of the tool kit"""
    show_tool_kit = Column(Boolean)
    """show_tool_kit - indicates whether the tool kit should be shown"""
    organisation_id = Column(Integer)
    """organisation_id - org id of the to which tool config is related"""

    tool_code_link = Column(String)
    """tool_code_link stores the link to the code repo of the tool"""

    def __repr__(self):
        return f"ToolKit(id={self.id}, name='{self.name}', description='{self.description}', " \
               f"show_tool_kit={self.show_tool_kit}," \
               f"organisation_id = {self.organisation_id}"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'show_tool_kit': self.show_tool_kit,
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
            show_tool_kit=data['show_tool_kit'],
            organisation_id=data['organisation_id']
        )

    @staticmethod
    def add_or_update(session, name, description, show_tool_kit, organisation_id, tool_code_link):
        # Check if the toolkit exists
        toolkit = session.query(ToolKit).filter(ToolKit.name == name, ToolKit.organisation_id == organisation_id).first()

        if toolkit:
            # Update the existing toolkit
            toolkit.name = name
            toolkit.description = description
            toolkit.show_tool_kit = show_tool_kit
            toolkit.organisation_id = organisation_id
            toolkit.tool_code_link = tool_code_link
        else:
            # Create a new toolkit
            toolkit = ToolKit(
                name=name,
                description=description,
                show_tool_kit=show_tool_kit,
                organisation_id=organisation_id,
                tool_code_link=tool_code_link
            )

            session.add(toolkit)

        session.commit()
        session.flush()
        print("NEW TOOL KIT MADE :",toolkit)
        return toolkit

    @classmethod
    def fetch_marketplace_list(cls, page):
        headers = {'Content-Type': 'application/json'}
        response = requests.get(
            marketplace_url + f"/tool_kits/marketplace/list/{str(page)}",
            headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return []

    @classmethod
    def fetch_marketplace_detail(cls, search_str, tool_kit_name):
        headers = {'Content-Type': 'application/json'}
        search_str = search_str.replace(' ', '%20')
        tool_kit_name = tool_kit_name.replace(' ', '%20')
        response = requests.get(
            marketplace_url + f"/tool_kits/marketplace/{search_str}/{tool_kit_name}",
            headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    @staticmethod
    def get_tool_kit_from_name(session, tool_kit_name):
        tool_kit = session.query(ToolKit).filter_by(name=tool_kit_name).first()
        if tool_kit:
            return tool_kit
        return None
