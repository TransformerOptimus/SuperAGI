from __future__ import annotations

from sqlalchemy import Column, Integer, String
import requests

# from superagi.models import AgentConfiguration
from superagi.models.base_model import DBBaseModel

#marketplace_url = "https://app.superagi.com/api"
marketplace_url = "http://localhost:3000/api"

class Knowledge(DBBaseModel):
    """
    Represents an knowledge entity.

    Attributes:
        id (int): The unique identifier of the knowledge.
        name (str): The name of the knowledge.
        description (str): The description of the knowledge.
        summary (str): The summary of the knowledge description.
        readme (str): The readme associated with the embedding.
        index_id (int): The index associated with the knowledge.
        is_deleted (int): The flag for deletion/uninstallation of a knowledge.
        organisation_id (int): The identifier of the associated organisation.
    """

    __tablename__ = 'knowledge'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    summary = Column(String)
    readme = Column(String)
    index_id = Column(Integer)
    organisation_id = Column(Integer)
    contributed_by = Column(String)

    def __repr__(self):
        """
        Returns a string representation of the Knowledge object.

        Returns:
            str: String representation of the Knowledge.

        """
        return f"Knowledge(id={self.id}, name='{self.name}', description='{self.description}', " \
               f"summary='{self.summary}', readme='{self.readme}', index_id={self.index_id}), " \
               f"organisation_id={self.organisation_id}), contributed_by={self.contributed_by}"

    @classmethod
    def fetch_marketplace_list(cls, session, page, organisation_id):
        page_size = 30

    # Apply search filter if provided
        query = session.query(Knowledge).filter(Knowledge.organisation_id == organisation_id)

    # Paginate the results
        knowledges = query.offset(page * page_size).limit(page_size).all()
        knowledge_data = []
        for knowledge in knowledges:
            data = {
                "id": knowledge.id,
                "name": knowledge.name,
                "description": knowledge.description,
                "summary": knowledge.summary,
                "readme": knowledge.readme,
                "index_id": knowledge.index_id,
                "organisation_id": knowledge.organisation_id,
                "contributed_by": knowledge.contributed_by
            }
            knowledge_data.append(data)
        return knowledge_data

    @classmethod
    def get_knowledge_installed_details(cls, session, marketplace_knowledges, organisation):
        installed_knowledges = session.query(Knowledge).filter(Knowledge.organisation_id == organisation.id).all()
        for knowledge in marketplace_knowledges:
            if knowledge['name'] in [installed_knowledges.name for installed_knowledge in installed_knowledges]:
                knowledge["is_installed"] = True
            else:
                knowledge["is_installed"] = False
        return marketplace_knowledges
    
    @classmethod
    def get_user_knowledge_list(cls, organisation_id):
        headers = {'Content-Type': 'application/json'}
        response = requests.get(
            marketplace_url + f"/knowledge/get/user/list/{organisation_id}",
            headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return []
        
    @classmethod
    def check_if_marketplace(cls, session, user_knowledge, marketplace_organisation_id):
        marketplace_knowledge = session.query(Knowledge).filter(Knowledge.organisation_id == marketplace_organisation_id, Knowledge.name == user_knowledge["name"]).first()
        if marketplace_knowledge:
            return True
        else:
            return False
        
    @classmethod
    def add_update_knowledge(session,knowledge_data):
        knowledge = session.query(Knowledge).filter(Knowledge.id == knowledge_data["id"],Knowledge.organisation_id == knowledge_data["organisation_id"])
        if knowledge:
            knowledge.name = knowledge_data["name"]
            knowledge.description = knowledge_data["description"]
            knowledge.summary = knowledge_data["summary"]
            knowledge.index_id = knowledge_data["index_id"]
        else:
            knowledge = Knowledge(name=knowledge_data["name"], description=knowledge_data["description"], summary = knowledge_data["summary"], readme=None, index_id = knowledge_data["index_id"], organisation_id = knowledge_data["organisation_id"], contributed_by= knowledge_data["contibuted_by"])
            session.add(knowledge)
        session.commit()
    