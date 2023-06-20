from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

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
            tool_kit_id (Integer): The identifier of the associated toolkit.
    """
    __tablename__ = 'tool_configs'


    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)
    tool_kit_id = Column(Integer)

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

    @staticmethod
    def add_or_update(session: Session, tool_kit_id: int, key: str, value: str = None):
        tool_config = session.query(ToolConfig).filter_by(tool_kit_id=tool_kit_id, key=key).first()
        if tool_config:
            # Update existing tool config
            if value is not None:
                tool_config.value = value
        else:
            # Create new tool config
            tool_config = ToolConfig(tool_kit_id=tool_kit_id, key=key, value=value)
            session.add(tool_config)

        session.commit()

    @staticmethod
    def get_tool_config_by_key(key: str, tool_kit_id: int,session: Session):
        tool_config = session.query(ToolConfig).filter_by(key=key, tool_kit_id=tool_kit_id).first()
        if tool_config:
            return tool_config.value
        # Read the config.yaml file
        with open("config.yaml") as file:
            config = yaml.safe_load(file)
        return config.get(key)
