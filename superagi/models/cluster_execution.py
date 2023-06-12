import json
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from superagi.models.base_model import DBBaseModel
from superagi.models.agent import Agent
from datetime import datetime


class ClusterExecution(DBBaseModel):
    __tablename__ = 'cluster_executions'

    id = Column(Integer, primary_key=True)
    status = Column(String)  # like ('CREATED', 'RUNNING', 'PAUSED', 'COMPLETED')
    name = Column(String)
    goal = Column(String)
    cluster_id = Column(Integer)
    last_execution_time = Column(DateTime)

    def __repr__(self):
        return f"AgentExecution(id={self.id}, name={self.name},status='{self.status}', " \
               f"last_execution_time='{self.last_execution_time}', goal='{self.goal}' , cluster_id={self.cluster_id})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'cluster_id': self.cluster_id,
            'last_execution_time': self.last_execution_time.isoformat()
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        last_execution_time = datetime.fromisoformat(data['last_execution_time'])
        return cls(
            id=data['id'],
            name=data['name'],
            status=data['status'],
            cluster_id=data['cluster_id'],
            last_execution_time=last_execution_time
        )