from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, sessionmaker

from superagi.models.base_model import DBBaseModel
import json
import yaml


class ToolConfig(DBBaseModel):
    """
        Model representing a tool configuration.

        Attributes:
            id (Integer): The primary key of the tool configuration.
            key (String): The key of the tool configuration.
            value (String): The value of the tool configuration.
            toolkit_id (Integer): The identifier of the associated toolkit.
    """
    __tablename__ = 'tool_configs'


    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)
    toolkit_id = Column(Integer)

    def __repr__(self):
        return f"ToolConfig(id={self.id}, key='{self.key}', value='{self.value}, toolkit_id={self.toolkit_id}')"

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'toolkit_id': {self.toolkit_id},
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
            toolkit_id=data['toolkit_id'],
        )

    @staticmethod
    def add_or_update(session: Session, toolkit_id: int, key: str, value: str = None):
        tool_config = session.query(ToolConfig).filter_by(toolkit_id=toolkit_id, key=key).first()
        if tool_config:
            # Update existing tool config
            if value is not None:
                tool_config.value = value
        else:
            # Create new tool config
            tool_config = ToolConfig(toolkit_id=toolkit_id, key=key, value=value)
            session.add(tool_config)

        session.commit()
