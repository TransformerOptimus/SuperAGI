from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from superagi.models.base_model import DBBaseModel
import json


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
    tool_readme_link = Column(String)
    """tool_readme_link stores the link of the readme of the tool  """
    # is_deleted = Column(Boolean)

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
