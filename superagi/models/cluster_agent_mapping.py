from sqlalchemy import Column, Integer, String, ForeignKey
from superagi.models.base_model import DBBaseModel
from superagi.models.project import Project
from sqlalchemy.orm import relationship


class ClusterAgentMapping(DBBaseModel):
    __tablename__ = 'cluster_agent_mapping'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(Integer, ForeignKey("agent_clusters.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)

    def __repr__(self):
        return f"ClusterAgentMapping(id={self.id}, name='{self.cluster_id}', project_id={self.agent_id}"
