import json

from sqlalchemy import Column, Integer, String

from superagi.models.base_model import DBBaseModel


class ToolStatistics(DBBaseModel):
    """ToolStatistics - used to store statistics for tool kits"""
    __tablename__ = 'tool_statistics'

    id = Column(Integer, primary_key=True)
    """id - id of the statistics entry"""
    toolkit_id = Column(Integer)
    """toolkit_id - foreign key reference to the tool kit"""

    key = Column(String)
    """key - key for the statistic"""
    value = Column(String)
    """value - value associated with the statistic"""

    def __repr__(self):
        return f"ToolStatistics(id={self.id}, toolkit_id={self.toolkit_id}, key='{self.key}', value='{self.value}')"

    def to_dict(self):
        return {
            'id': self.id,
            'toolkit_id': self.toolkit_id,
            'key': self.key,
            'value': self.value
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(
            id=data['id'],
            toolkit_id=data['toolkit_id'],
            key=data['key'],
            value=data['value']
        )
