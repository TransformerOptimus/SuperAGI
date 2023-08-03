from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Session, sessionmaker
from superagi.types.key_type import ToolConfigKeyType
from superagi.models.base_model import DBBaseModel
from superagi.helper.encyption_helper import encrypt_data
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
            key_type (String): the type of key used.
            is_secret (Boolean): Whether the tool configuration is a secret.
            is_required (Boolean): Whether the tool configuration is a required field.
    """
    __tablename__ = 'tool_configs'


    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)
    toolkit_id = Column(Integer)
    key_type = Column(String)
    is_secret = Column(Boolean)
    is_required = Column(Boolean)

    def __repr__(self):
        return f"ToolConfig(id={self.id}, key='{self.key}', value='{self.value}, toolkit_id={self.toolkit_id}')"

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'toolkit_id': {self.toolkit_id},
            'key_type': self.key_type,
            'is_secret': self.is_secret,
            'is_required': self.is_required
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
            key_type=data['key_type'],
            is_secret=data['is_secret'],
            is_required=data['is_required']
        )

    @staticmethod
    def add_or_update(session: Session, toolkit_id: int, key: str, value: str = None, key_type: str = None, is_secret: bool = False, is_required: bool = False):
        tool_config = session.query(ToolConfig).filter_by(toolkit_id=toolkit_id, key=key).first()
        if tool_config:
            # Update existing tool config
            if value is not None:
                tool_config.value = (value)

            if is_required is None:
                tool_config.is_required = False
            elif isinstance(is_required, bool):
                tool_config.is_required = is_required
            else:
                raise ValueError("is_required should be a boolean value")

            if is_secret is None:
                tool_config.is_secret = False
            elif isinstance(is_secret, bool):
                tool_config.is_secret = is_secret
            else:
                raise ValueError("is_secret should be a boolean value")

            if key_type is None:
                tool_config.key_type = ToolConfigKeyType.STRING.value
            elif isinstance(key_type,ToolConfigKeyType):
                tool_config.key_type = key_type.value
            else:
                tool_config.key_type = key_type

        else:
            # Create new tool config
            if key_type is None:
                key_type = ToolConfigKeyType.STRING.value
            if isinstance(key_type,ToolConfigKeyType):
                key_type = key_type.value    
            tool_config = ToolConfig(toolkit_id=toolkit_id, key=key, value=value, key_type=key_type, is_secret=is_secret, is_required=is_required)
            session.add(tool_config)

        session.commit()

    @classmethod
    def get_toolkit_tool_config(cls, session: Session, toolkit_id: int):
        return session.query(ToolConfig).filter_by(toolkit_id=toolkit_id).all()
