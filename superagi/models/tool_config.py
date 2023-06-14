from sqlalchemy import Column, Integer, String
from superagi.models.base_model import DBBaseModel
import json


class ToolConfig(DBBaseModel):
    """ToolConfig - used to store tool configurations"""
    __tablename__ = 'tool_configs'

    id = Column(Integer, primary_key=True)
    """id - id of the tool config"""
    key = Column(String)
    """key - configuration key"""
    value = Column(String)
    """value - configuration value"""
    tool_kit_id = Column(Integer)
    """tool_config_id - foreign key referencing the tool configuration"""

    def __repr__(self):
        return f"ToolConfig(id={self.id}, key='{self.key}', value='{self.value}, tool_kit_id={self.tool_kit_id}')"

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'tool_kit_id': {self.tool_kit_id},
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(
            id=data['id'],
            key=data['key'],
            value=data['value'],
            tool_kit_id=data['tool_kit_id'],
        )
