from __future__ import annotations

from sqlalchemy import Column, Integer, String

# from superagi.models import AgentConfiguration
from superagi.models.base_model import DBBaseModel


class Vectordb(DBBaseModel):
    """
    Represents an vector db entity.

    Attributes:
        id (int): The unique identifier of the agent.
        name (str): The name of the agent.
        organisation_id (int): The identifier of the associated organisation.
    """

    __tablename__ = 'vector_db'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    organisation_id = Column(Integer)

    def __repr__(self):
        """
        Returns a string representation of the Vector db object.

        Returns:
            str: String representation of the Vector db.

        """
        return f"Vector(id={self.id}, name='{self.name}', organisation_id={self.organisation_id}"#, " \
               #f"description='{self.description}', agent_workflow_id={self.agent_workflow_id})"



    @classmethod
    def fetch_marketplace_list(cls, page):
        headers = {'Content-Type': 'application/json'}
        response = requests.get(
            marketplace_url + f"/vectordb/marketplace/list/{str(page)}",
            headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return []
